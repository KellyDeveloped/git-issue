from pathlib import Path
from utils.json_utils import JsonConvert
from git_manager import GitManager

@JsonConvert.register
class UUIDTrack(object):

    def __init__(self, uuid=None, issue=None):
        self.uuid = uuid
        self.issue = issue

    def __eq__(self, value):
        if type(value) is UUIDTrack:
            return self.uuid == value.uuid and self.issue == value.issue

        return False

    def __hash__(self):
        return self.issue.__hash__() + self.uuid.__hash__()


@JsonConvert.register
class Tracker(object):
    """All non-user tracked settings (i.e program-defined variables) are contained here."""

    ISSUE_IDENTIFIER = "ISSUE"

    def __init__(self, issue_count=0, tracked_uuids:[UUIDTrack]=[]):
        self.issue_count = issue_count
        self.tracked_uuids = tracked_uuids

    def increment_issue_count(self):
        self.issue_count += 1

    def track_or_update_uuid(self, uuid, issue):
        for tracked in self.tracked_uuids:
            if tracked.uuid == uuid:
                tracked.issue = issue
                return
        
        self.tracked_uuids.append(UUIDTrack(uuid, issue))

    def get_issue_from_uuid(self, uuid):
        for tracked in self.tracked_uuids:
            if tracked.uuid == uuid:
                return tracked.issue

        return None

    def store_tracker(self):
        JsonConvert.ToFile(self, Tracker.get_path())
        gm = GitManager()
        gm.add_to_index([str(Tracker.get_path())])

    @classmethod
    def get_path(cls):
        return Path.cwd().joinpath("tracker.json")

    @classmethod
    def obtain_tracker(cls):
        tracker = None    
        path = cls.get_path()

        if path.exists():
            tracker = JsonConvert.FromFile(path)
        else:
            tracker = Tracker()

        return tracker

