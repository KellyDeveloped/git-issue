from GitUser import Gituser
import Comment

class Issue(object):
    """This class encapsulates what an issue is, and provides utility methods to """

    def __init__(self):
        self.id = ""
        self.summary = ""
        self.description = ""
        self.comments = []
        self.status = ""
        self.assignee = GitUser()
        self.reporter = GitUser()
        self.subscribers = []
        self.attachments = []
