import git
from enum import Enum
from abc import ABC, abstractmethod

from git import Repo
from pathlib import Path

from utils.json_utils import JsonConvert
from issue.issue import Issue
from issue.tracker import Tracker
from comment.index import Index

class ConflictType(enum):
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

class GitMerge(object):
    """ A class designed to """

    def __init__(self, repo: Repo):
        self.repo = repo

    def get_conflicts(self) -> [ConflictInfo]:
        conflicts = []
        createConflicts = []
        trackerConflicts = []
        commentConflicts = []
        manualConflicts = []

        unmerged_blobs = self.repo.index.unmerged_blobs()
        for unmerged_file in unmerged_blobs:
            for (stage, blob) in unmerged_blobs[unmerged_file]:
                if stage != 0:
                    data = blob.data_stream.read().decode()
                    obj = JsonConvert.FromJSON(data);

                    conflict = ConflictInfo(unmerged_file, obj)

                    if conflict.type is ConflictType.CREATE:
                        createConflicts.append(conflict)

                    elif conflict.type is ConflictType.TRACKER:
                        """ 
                            tracker is only ever updated on create/create conflict resolution 
                            We don't need to bother with it as create will reconstruct any data changes
                        """
                        pass 

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
