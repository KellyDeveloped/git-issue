from uuid import uuid4
from git_issue.gituser import GitUser
from git_issue.utils.json_utils import JsonConvert
from git_issue.utils import date_utils


@JsonConvert.register
class Issue(object):
    """This class encapsulates what an issue is, and may provide supporting methods for issues."""

    def __init__(self, id:str=None, date=date_utils.get_date_now(), uuid=None, summary:str=None,
                description:str=None, status:str="open", assignee:GitUser=None,
                reporter:GitUser=None, subscribers=[], attachments=[]):
        self.id = id
        self.uuid = uuid if uuid is not None else uuid4().int
        self.date = date
        self.summary = summary
        self.description = description
        self.status = status
        self.assignee: GitUser = assignee
        self.reporter: GitUser = reporter
        self.subscribers: [GitUser] = subscribers
        self.attachments = attachments

    def display(self):
        print(f"Issue ID:\t{self.id}")
        print(f"Summary:\t{self.summary}")
        print(f"Description:\t{self.description}")

        print(f"Status:\t\t{self.status}")

        if self.assignee != None:
            print(f"Assignee:\t{self.assignee.user}, {self.assignee.email}")
        else:
            print("Assignee:\tUnassigned")

        if self.reporter != None:
            print(f"Reporter:\t{self.reporter.user}, {self.reporter.email}")
        else:
            print("Reporter:\tUnassigned")

        print("Subscribers:")
        for s in self.subscribers:
            print(f"\t{s.user}, {s.email}")

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