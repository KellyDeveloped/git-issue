from gituser import GitUser
from comment import Comment
import jsonutils

@jsonutils.JsonConvert.register
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
