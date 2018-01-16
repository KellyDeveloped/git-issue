from jsonutils import JsonConvert
import os

@JsonConvert.register
class Tracker(object):
    """All non-user tracked settings (i.e program-defined variables) are contained here."""

    ISSUE_IDENTIFIER = "ISSUE"
    path = os.path.normpath(os.getcwd() + "/tracker.json")

    def __init__(self):
        self.issue_count = 0
        
    def increment_issue_count(self):
        self.issue_count += 1

    def store_tracker(self):
        JsonConvert.ToFile(self, path)

    @classmethod
    def obtain_tracker(cls):
        tracker = None
    
        if os.path.exists(cls.path):
            tracker = JsonConvert.FromFile(cls.path)
        else:
            tracker = Tracker()

        return tracker