import uuid
from gituser import GitUser
from utils.json_utils import JsonConvert
from utils import date_utils


@JsonConvert.register
class Issue(object):
    """This class encapsulates what an issue is, and may provide supporting methods for issues."""

    def __init__(self, id:str=None, date=date_utils.get_date_now(), uuid=uuid.uuid4().int, summary:str=None,
                description:str=None, status:str="open", assignee:GitUser=None,
                reporter:GitUser=None, subscribers=[], attachments=[]):
        self.id = id
        self.uuid = uuid
        self.date = date
        self.summary = summary
        self.description = description
        self.status = status
        self.assignee: GitUser = assignee
        self.reporter: GitUser = reporter
        self.subscribers: [GitUser] = subscribers
        self.attachments = attachments

    def __eq__(self, other: object) -> bool:
        if type(other) is not Issue:
            return False

        o: Issue = other

        return self.id == o.id and self.uuid == o.uuid and\
            self.date == o.date and self.summary == o.summary and\
            self.description == o.description and self.status == o.status and\
            self.assignee == o.assignee and self.reporter == o.reporter and\
            self.subscribers == o.subscribers

status_indicators = ["open", "closed", "in progress"]