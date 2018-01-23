from git_issue.gituser import GitUser
from git_issue.comment import Comment
from git_issue.json_utils import JsonConvert

@JsonConvert.register
class Issue(object):
    """This class encapsulates what an issue is, and provides utility methods to """

    def __init__(self, id=None, summary=None, description=None, comments=[],
                status=None, assignee=None, reporter=None,
               subscribers=[], attachments=[]):
        self.id = id
        self.summary = summary
        self.description = description
        self.comments:[Comment] = comments
        self.status = status
        self.assignee:GitUser = assignee
        self.reporter:GitUser = reporter
        self.subscribers:[GitUser] = subscribers
        self.attachments = attachments
