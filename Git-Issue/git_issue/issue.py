from git_issue.gituser import GitUser
from git_issue.comment import Comment
from git_issue.json_utils import JsonConvert

@JsonConvert.register
class Issue(object):
    """This class encapsulates what an issue is, and provides utility methods to """

    def __init__(self):
        self.id = ""
        self.summary = ""
        self.description = ""
        self.comments:[Comment] = []
        self.status = ""
        self.assignee:GitUser = None
        self.reporter:GitUser = None
        self.subscribers:[GitUser] = []
        self.attachments = []
