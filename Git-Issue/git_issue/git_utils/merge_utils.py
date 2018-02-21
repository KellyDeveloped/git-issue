import git
from enum import Enum
from abc import ABC, abstractmethod

from git import Repo
from pathlib import Path

from git_manager import GitManager
from utils.json_utils import JsonConvert
from issue.issue import Issue
from issue.handler import IssueHandler
from issue.tracker import Tracker
from comment.index import Index

class ConflictType(Enum):
    CREATE = 1
    TRACKER = 2
    COMMENT_INDEX = 3
    MANUAL = 4 # Reserved for things we can't resolve

class ConflictInfo(object):

    def __init__(self, path: Path, conflicts: []):
        self.path = path
        self.conflicts = conflicts
        self.type = self._determine_type()

    def _determine_type(self) -> ConflictType:
        conflictType = type(self.conflicts)
        if conflictType is [Issue]:
            uuids = [issue.uuid for issue in self.conflicts]

            # If the unique ID's are all the same then it's been an edit
            if len(set(uuids)) > 1:
                return ConflictType.CREATE

        elif conflictType is [Tracker]:
            return ConflictType.TRACKER

        elif conflictType is [Index]:
            return ConflictType.COMMENT_INDEX
        
        return ConflictType.MANUAL

class ResolutionTool(ABC):
    
    @abstractmethod
    def resolve(self):
        pass

class CreateResolutionTool(ResolutionTool):

    def __init__(self, resolved_issues: [Issue, string], tracker: Tracker):
        self.resolved_issues = issues
        self.tracker = tracker

    def resolve(self):
        gm = GitManager()
        paths = []

        for issue, path in self.resolved_issues:
            JsonConvert.ToFile(issue, path)
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
    def generateResolution(self) -> ResolutionTool:
        pass

class CreateConflictResolver(ConflictResolver):
    """
        Class designed to record conflicting create statements and resolve them when
        called upon
    """

    def __init__(self):
        self.conflicts : [Issue, string] = []
        self.tracker : Tracker = None

    def generateResolution(self):
        """ 
            Resolves conflicts by re-ordering the issues based on their creation date.
            The conflicts are resolved by giving the oldest issue the first conflicting issue ID.

            Returns a tuple containing the list of resolved conflicts, and an updated tracker.
            These resolved conflicts are NOT stored to fie by this method. This is left as a job for the consumer.
        """

        # Create copies of data to avoid mutating them as a side affect
        issues = self.conflicts.copy()
        tracker = Tracker(self.tracker.issue_count, self.tracker.tracked_uuids.copy())

        issues.sort(key=lambda x, y : x.date)
        issue_ids = [id for issue.id in issues]

        for issue, path in issues, id in issue_ids:
            issue.id = id
            tracker.track_or_update_uuid(issue.uuid, id)

        return CreateResolutionTool(issues, tracker)

class CommentIndexConflictResolver(ConflictResolver):
    
    def __init__(self):
        self.conflict : [Index] = None
        self.path : Path = None

    def generateResolution(self):
        entries = []

        for conflict in self.conflicts:
            entries += conflict.entries

        entries = list(set(entries)) # remove duplicates by converting to set and back to list
        entries.sort(key=lambda x: x.date)
        self.index.entries = entries

        return CommentIndexResolutionTool(self.index, self.path)

class GitMerge(object):
    """ A class designed to """

    def __init__(self, repo: Repo):
        self.repo = repo

    def get_conflicts(self) -> [ConflictInfo]:
        createConflicts = []
        commentConflicts = []
        manualConflicts = []

        unmerged_blobs = self.repo.index.unmerged_blobs()
        for unmerged_file in unmerged_blobs:
            conflicts = []

            for (stage, blob) in unmerged_blobs[unmerged_file]:
                data = blob.data_stream.read().decode()
                obj = JsonConvert.FromJSON(data)
                
                # A stage of one means a common ancestor.
                if type(obj) is Issue and stage == 1:
                    manualConflicts.append(obj)
                    break
                conflicts.append(obj)

            info = ConflictInfo(unmerged_file, conflicts)

            elif stage != 0:
                data = blob.data_stream.read().decode()
                obj = JsonConvert.FromJSON(data)

                conflict = ConflictInfo(unmerged_file, obj)

                if conflict.type is ConflictType.CREATE:
                    createConflicts.append(conflict)

                elif conflict.type is ConflictType.TRACKER:
                    if stage == 1:
                        pass  # TODO: Put the tracker into the CreateConflictResolver

                elif conflict.type is ConflictType.COMMENT_INDEX:
                    commentConflicts.append(conflict)

                else:
                    manualConflicts.append(conflict)

            for (stage, blob) in unmerged_blobs[unmerged_file]:
                data = blob.data_stream.read().decode()
                obj = JsonConvert.FromJSON(data)

                # A stage of one means a common ancestor.
                if type(obj) is Issue and stage == 1:
                    manualConflicts.append(obj)
                    break

                elif stage != 0:
                    data = blob.data_stream.read().decode()
                    obj = JsonConvert.FromJSON(data)

                    conflict = ConflictInfo(unmerged_file, obj)

                    if conflict.type is ConflictType.CREATE:
                        createConflicts.append(conflict)

                    elif conflict.type is ConflictType.TRACKER:
                        if stage == 1:
                            pass  # TODO: Put the tracker into the CreateConflictResolver

                    elif conflict.type is ConflictType.COMMENT_INDEX:
                        commentConflicts.append(conflict)

                    else:
                        manualConflicts.append(conflict)

            conflicts.append(ConflictInfo(unmerged_file, obj))
        return conflicts    

    def is_resolvable(self, conflict: ConflictInfo):
        pass

    def get_strategy(self):
        pass

class MergeStrategy(ABC):
    pass

class CreateConflictStrategy(MergeStrategy):

    def __init__(self, conflict: ConflictInfo):
        if conflict.type is not ConflictType.CREATE:
            raise TypeError(f"CreateConflictStrategy cannot resolve conflict type {ConflictInfo.type.name}")

        self.conflict = conflict
