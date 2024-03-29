from git_issue.gituser import GitUser
from git_issue.utils import date_utils
from git_issue.utils.json_utils import JsonConvert
import uuid as unique_identifier

@JsonConvert.register
class Comment(object):
    """ Class represents what a comment is. The default date of a comment is the current datetime
        in UTC formatted as ISO. As issue contributors may be situated all across the world,
        using their system time could be dangerous. 
        
        For example, if someone from Bangalore were to make a comment and synchronise with the 
        repository, and then immediately after someone from New York were to then add another
        comment the New York's user would appear to be made before the Bangalore comment due
        to it being in an earlier timezone. """

    def __init__(self, comment: str="", user: GitUser=None, date=None, uuid=None):
        self.comment = comment
        self.user = user if user is not None else GitUser()
        self.date = date if date is not None else date_utils.get_date_now()
        self.uuid = uuid if uuid is not None else unique_identifier.uuid4().int
