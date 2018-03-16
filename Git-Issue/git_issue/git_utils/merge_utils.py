from copy import deepcopy

from enum import Enum
from abc import ABC, abstractmethod

from git import Repo
from pathlib import Path
from typing import List

from git_issue.git_manager import GitManager
from git_issue.utils.json_utils import JsonConvert
from git_issue.issue.issue import Issue
from git_issue.issue.handler import IssueHandler
from git_issue.issue.tracker import Tracker, UUIDTrack
from git_issue.comment.index import Index


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

    def __init__(self, resolved_issues: [(Issue, str)], tracker: Tracker):
        self.resolved_issues = resolved_issues
        self.tracker = tracker

    def resolve(self):
        gm = GitManager()
        paths = []

        gm.load_issue_branch()
        for issue in self.resolved_issues:
            handler = IssueHandler(self.tracker)
            file_path = handler.get_issue_path(issue)
            JsonConvert.ToFile(issue, file_path)
            paths.append(str(file_path))

        self.tracker.store_tracker()

        repo = gm.obtain_repo()
        for path in paths:
            repo.git.add(path)


class CommentIndexResolutionTool(ResolutionTool):
    
    def __init__(self, resolved_index: Index, path: Path):
        self.index = resolved_index
        self.path = path

    def resolve(self):
        JsonConvert.ToFile(self.index, Path(self.path))
        gm = GitManager()
        repo = gm.obtain_repo()
        repo.git.add(self.path)

class DivergenceResolutionTool(ResolutionTool):

    def __init__(self, resolved_issues: [Issue]):
        self.resolved_issues = resolved_issues

    def resolve(self):
        gm = GitManager()
        gm.load_issue_branch()
        paths = []
        handler = IssueHandler()

        for issue in self.resolved_issues:
            file_path = handler.get_issue_path(issue)
            JsonConvert.ToFile(issue, file_path)
            paths.append(str(file_path))

        repo = gm.obtain_repo()
        for path in paths:
            repo.git.add(path)

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
        self.conflicts: [ConflictInfo] = []
        self.tracker: Tracker = None

    def generate_resolution(self):
        """
            Resolves conflicts by re-ordering the issues based on their creation date.
            The conflicts are resolved by giving the oldest issue the first conflicting issue ID.

            Returns a tuple containing the list of resolved conflicts, and an updated tracker.
            These resolved conflicts are NOT stored to fie by this method. This is left as a job for the consumer.
        """

        # Create copies of data to avoid mutating them as a side affect
        conflicts = []

        for info in self.conflicts:
            for issue in info.conflicts:
                conflicts.append(issue)

        if self.tracker is None:
            tracker = Tracker.obtain_tracker()
        else:
            tracker = Tracker(self.tracker.issue_count, self.tracker.tracked_uuids.copy())

        complete = False
        handler = IssueHandler(tracker)
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
        self.conflict_info: ConflictInfo = None

    def generate_resolution(self):
        entries = []

        for conflict in self.conflict_info.conflicts:
            entries += conflict.entries

        entries = list(set(entries)) # remove duplicates by converting to set and back to list
        entries.sort(key=lambda x: x.date)
        index = Index(entries)

        return CommentIndexResolutionTool(index, self.conflict_info.path)


class DivergenceConflictResolver(ConflictResolver):

    def __init__(self):
        self.diverged_issues = []
        self.resolved_conflicts: [Issue] = []
        self.resolved_tracker: Tracker

    def _get_edit_resolution(self, diverged: Issue, current: Issue) -> Issue:
        print(f"Issue with ID {diverged.id} and UUID {diverged.uuid} has been changed to {current.id} in a previous "
              f"merge conflict resolution.")

        print("Please examine the two issues and give a resolution to the conflicts when prompted")
        print("\nHEAD:-")
        current.display()
        print("\nMERGE HEAD:-")
        diverged.display()
        updated_issue = deepcopy(current)

        diverged.id = current.id

        fields = self._get_edited_fields(diverged, current)
        for field, div, curr in fields:
            edit = input(f"Resolution for {field}:")
            setattr(updated_issue, field, edit)

        return updated_issue

    def _get_edited_fields(self, diverged, current):
        diff = []

        for d in diverged.__dict__:
            div_attr = getattr(diverged, d)
            cur_attr = getattr(current, d)

            if div_attr != cur_attr:
                diff.append((d, div_attr, cur_attr))

        return diff

    def generate_resolution(self):
        matching_issues: (Issue, Issue) = []
        diverged_issues = self.diverged_issues
        resolved_issues = []

        for resolved in self.resolved_conflicts:
            found = False
            diverged_index = 0

            for stage_2, stage_3 in diverged_issues:
                match = None

                if stage_2.uuid == resolved.uuid and stage_2.id != resolved.id:
                    match = stage_2
                    resolved_issues.append(stage_3)
                elif stage_3.uuid == resolved.uuid and stage_3.id != resolved.id:
                    match = stage_3
                    resolved_issues.append(stage_2)

                if match is not None:
                    found = True
                    matching_issues.append((match, resolved))
                    break
                diverged_index += 1

            if found: # Remove the found issue from the list so we don't need to examine it again
                del diverged_issues[diverged_index]

        handler = IssueHandler(self.resolved_tracker)

        for stage_2, stage_3 in diverged_issues:
            loaded_stage_2 = handler.get_issue_from_uuid(stage_2.uuid)
            loaded_stage_3 = handler.get_issue_from_uuid(stage_3.uuid)

            if loaded_stage_2 is not None:
                matching_issues.append((stage_2, loaded_stage_2))
                resolved_issues.append(stage_3)
            elif loaded_stage_3 is not None:
                matching_issues.append((stage_3, loaded_stage_3))
                resolved_issues.append(stage_2)
            else:
                raise DivergenceMatchMissingError(stage_2, stage_3, "Failed to discern the stage that is diverged")

        if len(matching_issues) > 0:
            print("One or more create-edit divergencies have been identified. This is when an issue on "\
                "one branch has been edited, after it has been resolved as a create conflict "\
                "on another branch that is being merged with the current branch.")

            for diverged, match in matching_issues:
                resolved = self._get_edit_resolution(diverged, match)
                resolved_issues.append(resolved)

        resolution = DivergenceResolutionTool(resolved_issues)

        return resolution


class GitMerge(object):
    """ A class designed to """

    def __init__(self, repo: Repo):
        self.repo = repo

    def _get_conflicts_of_type(self, type: ConflictType, conflicts: [ConflictInfo] = None):
        if conflicts is None or conflicts == []:
            conflicts = self.parse_unmerged_conflicts()

        return [conflict for conflict in conflicts if conflict.type is type]

    def has_conflicts(self) -> bool:
        return self.repo.index.unmerged_blobs() != {}

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

    def produce_create_resolver(self, conflicts: [ConflictInfo] = None) -> ConflictResolver:
        resolver = CreateConflictResolver()
        resolver.conflicts = self._get_conflicts_of_type(ConflictType.CREATE, conflicts)

        uuids = []

        for info in resolver.conflicts:
            uuids = [UUIDTrack(issue.uuid, issue.id) for issue in info.conflicts]

        resolver.tracker = Tracker(len(uuids), uuids)
        return resolver

    def produce_comment_index_resolvers(self, conflicts: [ConflictInfo] = None) -> List[ConflictResolver]:
        comment_conflicts = self._get_conflicts_of_type(ConflictType.COMMENT_INDEX, conflicts)
        resolvers: List[ConflictResolver] = []

        for conflict in comment_conflicts:
            resolver = CommentIndexConflictResolver()
            resolver.conflict_info = conflict
            resolvers.append(resolver)

        return resolvers

    def produce_create_edit_divergence_resolver(self, conflicts: [ConflictInfo],
                                                resolved_issues: [Issue],
                                                resolved_tracker: Tracker) -> ConflictResolver:
        diverged_conflicts = self._get_conflicts_of_type(ConflictType.CREATE_EDIT_DIVERGENCE, conflicts)
        diverged_issues = []

        for info in diverged_conflicts:
            # Head should always equal common ancestor, but in the event it's ever the merge head that equals
            # the common ancestor and not the head then we need to work from that instead. Branch should never
            # be hit, but is there as a safety precaution
            diverged = (info.conflicts[1], info.conflicts[2])
            diverged_issues.append(diverged)

        resolver = DivergenceConflictResolver()
        resolver.diverged_issues = diverged_issues
        resolver.resolved_conflicts = resolved_issues
        resolver.resolved_tracker = resolved_tracker

        return resolver

    def filter_manual_conflicts(self, conflicts: [ConflictInfo] = None):
        return self._get_conflicts_of_type(ConflictType.MANUAL, conflicts)


class DivergenceMatchMissingError(Exception):

    def __init__(self, stage_2: Issue, stage_3: Issue, message):
        message += f"\n\nstage_2: {stage_2.id}, {stage_2.uuid}\nStage 3: {stage_3.id}, {stage_3.uuid}"

        super(Exception, self).__init__(message)
        self.stage_2 = stage_2
        self.stage_3 = stage_3
