import git
from enum import Enum
from abc import ABC, abstractmethod

from git import Repo
from pathlib import Path

from git_manager import GitManager
from utils.json_utils import JsonConvert
from issue.issue import Issue
from issue.handler import IssueHandler
from issue.tracker import Tracker, UUIDTrack
from comment.index import Index


class ConflictType(Enum):
    CREATE = 1
    TRACKER = 2
    COMMENT_INDEX = 3
    MANUAL = 4  # Reserved for things we can't resolve
    CREATE_EDIT_DIVERGENCE = 5  # For when there's been an edit on an already-resolved create conflict


class ConflictInfo(object):

    def __init__(self, path: Path, conflicts: []):
        self.path = path
        self.conflicts = conflicts
        self.type = self._determine_type()

    def _determine_type(self) -> ConflictType:
        conflictType = type(self.conflicts[0])
        if conflictType is Issue:
            uuids = [issue.uuid for issue in self.conflicts]

            no_of_uuids = len(set(uuids))

            # If we have two different UUID's but three stages then create-edit
            # divergence has occured
            if no_of_uuids == 2 and len(uuids) == 3:
                return ConflictType.CREATE_EDIT_DIVERGENCE

            # If the unique ID's are all the same then it's been an edit
            if len(set(uuids)) > 1:
                return ConflictType.CREATE

        elif conflictType is Tracker:
            return ConflictType.TRACKER

        elif conflictType is Index:
            return ConflictType.COMMENT_INDEX
        
        return ConflictType.MANUAL

    def __eq__(self, object: object) -> bool:
        if type(object) is not ConflictInfo:
            return False

        return self.conflicts == object.conflicts and self.path == object.path\
               and self.type is object.type


class ResolutionTool(ABC):
    
    @abstractmethod
    def resolve(self):
        pass


class CreateResolutionTool(ResolutionTool):

    def __init__(self, resolved_issues: [Issue, str], tracker: Tracker):
        self.resolved_issues = resolved_issues
        self.tracker = tracker

    def resolve(self):
        gm = GitManager()
        paths = []

        for issue, path in self.resolved_issues:
            file_path = Path(path)
            JsonConvert.ToFile(issue, file_path)
            paths.append(path)

        self.tracker.store_tracker()
        gm.add_to_index(paths)
        gm.commit("create-conflict-resolution")


class CommentIndexResolutionTool(ResolutionTool):
    
    def __init__(self, resolved_index: Index, path: Path):
        self.index = resolved_index
        self.path = path

    def resolve(self):
        self.index.set_index_path(self.path)
        self.index.store_index()


class ConflictResolver(ABC):

    @abstractmethod
    def generate_resolution(self) -> ResolutionTool:
        pass


class CreateConflictResolver(ConflictResolver):
    """
        Class designed to record conflicting create statements and resolve them when
        called upon
    """

    def __init__(self):
        self.conflicts: [Issue] = []
        self.tracker: Tracker = None

    def generate_resolution(self):
        """ 
            Resolves conflicts by re-ordering the issues based on their creation date.
            The conflicts are resolved by giving the oldest issue the first conflicting issue ID.

            Returns a tuple containing the list of resolved conflicts, and an updated tracker.
            These resolved conflicts are NOT stored to fie by this method. This is left as a job for the consumer.
        """

        # Create copies of data to avoid mutating them as a side affect
        conflicts = self.conflicts.copy()

        if self.tracker is None:
            tracker = Tracker.obtain_tracker()
        else:
            tracker = Tracker(self.tracker.issue_count, self.tracker.tracked_uuids.copy())

        complete = False
        handler = IssueHandler()
        ids = [issue.id for issue in conflicts]

        while not complete:
            to_add = []

            for issue in conflicts:
                next_id = handler.next_issue_id(issue)

                if next_id not in ids:
                    if handler.does_issue_exist(next_id):
                        missing = handler.get_issue_from_issue_id(next_id)
                        to_add.append(missing)

                    ids.append(next_id)

            for issue in to_add:
                conflicts.append(issue)
                ids.append(issue.id)

            complete = len(to_add) == 0

        conflicts.sort(key=lambda x: x.date)
        sorted_ids = list(set(ids))
        sorted_ids.sort()

        assert len(sorted_ids) == len(conflicts)

        index = 0
        for id in sorted_ids:
            issue = conflicts[index]
            issue.id = id
            tracker.track_or_update_uuid(issue.uuid, id)
            index += 1

        return CreateResolutionTool(conflicts, tracker)


class CommentIndexConflictResolver(ConflictResolver):
    
    def __init__(self):
        self.conflicts : [Index] = None
        self.path : Path = None

    def generate_resolution(self):
        entries = []

        for conflict in self.conflicts:
            entries += conflict.entries

        entries = list(set(entries)) # remove duplicates by converting to set and back to list
        entries.sort(key=lambda x: x.date)
        index = Index(entries)

        return CommentIndexResolutionTool(index, self.path)

class DivergenceConflictResolver(ConflictResolver):

    def __init__(self):
        self.diverged_issues = []
        self.resolved_conflicts: [Issue] = []
        self.resolved_tracker: Tracker = None

    def _get_edit_resolution(self, diverged, current):
        print(f"Issue with ID {diverged.id} and UUID {diverged.uuid} is conflicting with issue {current.id}")
        print("The following are the conflicts between the ")

    def generate_resolution(self):
        matching_issues: (Issue, Issue) = []
        diverged_issues = self.diverged_issues

        for resolved in self.resolved_conflicts:
            found = False
            diverged_index = 0

            for diverged in diverged_issues, i in range(0, len(diverged_issues)):
                if diverged.uuid == resolved.uuid:
                    found = True
                    diverged_index = i
                    matching_issues.append(diverged, resolved)
                    break

            if found: # Remove the found issue from the list so we don't need to examine it again
                del diverged_issues[diverged_index]

        handler = IssueHandler(self.resolved_tracker)
        matching_issues += [(diverged, handler.get_issue_from_uuid(diverged.uuid)) for diverged in diverged_issues]

        print("One or more create-edit divergencies have been identified. This is when an issue on "\
            "one branch has been edited, after it has been resolved as a create conflict "\
            "on another branch that is being merged with the current branch.")

        for diverged, match in matching_issues:
            self._get_edit_resolution(diverged, match)

class GitMerge(object):
    """ A class designed to """

    def __init__(self, repo: Repo):
        self.repo = repo

    def _get_conflicts_of_type(self, type: ConflictType, conflicts: [ConflictInfo] = None):
        if conflicts is None or conflicts == []:
            conflicts = self.parse_unmerged_conflicts()

        return [conflict for conflict in conflicts if conflict.type is type]

    def parse_unmerged_conflicts(self) -> [ConflictInfo]:
        unmerged_blobs = self.repo.index.unmerged_blobs()
        unmerged: [ConflictInfo] = []

        for unmerged_file in unmerged_blobs:
            conflicts = []

            for (stage, blob) in unmerged_blobs[unmerged_file]:
                if stage != 0:
                    data = blob.data_stream.read().decode()
                    obj = JsonConvert.FromJSON(data)

                    conflicts.append(obj)

            unmerged.append(ConflictInfo(unmerged_file, conflicts))

        return unmerged

    def produce_create_resolver(self, conflicts: [ConflictInfo] = None) -> CreateConflictResolver:
        resolver = CreateConflictResolver()
        resolver.conflicts = self._get_conflicts_of_type(ConflictType.CREATE, conflicts)

        for info in resolver.conflicts:
            uuids = [UUIDTrack(issue.uuid, issue.id) for issue in info.conflicts]

        resolver.tracker = Tracker(len(uuids), uuids)
        return resolver

    def produce_comment_index_resolver(self, path: Path, conflicts: [ConflictInfo] = None):
        resolver = CommentIndexConflictResolver()
        resolver.conflicts = self._get_conflicts_of_type(ConflictType.COMMENT_INDEX, conflicts)
        resolver.path = path
        return resolver

    def begin_conflict_resolution(self) -> [ConflictInfo]:
        indexConflicts = CommentIndexConflictResolver()
        createConflicts = CreateConflictResolver()
        divergenceConflict = DivergenceConflictResolver()
        manualConflicts = []

        unmerged_blobs = self.repo.index.unmerged_blobs()
        for unmerged_file in unmerged_blobs:
            conflicts = []

            for (stage, blob) in unmerged_blobs[unmerged_file]:
                if stage != 0:
                    data = blob.data_stream.read().decode()
                    obj = JsonConvert.FromJSON(data)

                    conflicts.append(obj)

            info = ConflictInfo(unmerged_file, conflicts)

            if info.type is ConflictType.CREATE:
                createConflicts.conflicts.append(info)

            elif info.type is ConflictType.CREATE_EDIT_DIVERGENCE:
                diverged = info.conflicts[1] if info.conflicts[0] == info.conflicts[1] else info.conflicts[2]
                divergenceConflict.diverged_issues.append(diverged)

            elif info.type is ConflictType.TRACKER:
                if len(info.conflicts) == 3:
                    createConflicts.tracker = info.conflicts[0]
                else:
                    tracked = [tracker.tracked_uuids for tracker in conflicts]
                    unique = list(set(tracked))

                    createConflicts.tracker = Tracker(len(unique), unique)
                    
            # elif info.type is ConflictType.COMMENT_INDEX:
                # indexConflicts.conflicts.append(conflict)

            # else:
            #     manualConflicts.append(conflict)

        for conflict in createConflicts.conflicts:
            print (f"{conflict.id} || {conflict.uuid} || {conflict.date}")

        conflictResolution = createConflicts.generate_resolution()

        for resolution in conflictResolution:
            print (f"{resolution.id} || {resolution.uuid} || {resolution.date}")

        return manualConflicts