from pathlib import Path
from git_issue.json_utils import JsonConvert

@JsonConvert.register
class Tracker(object):
    """All non-user tracked settings (i.e program-defined variables) are contained here."""

    ISSUE_IDENTIFIER = "ISSUE"

    def __init__(self, issue_count=0):
        self.issue_count = issue_count
        
    def increment_issue_count(self):
        self.issue_count += 1

    def store_tracker(self):
        JsonConvert.ToFile(self, Tracker.get_path())

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