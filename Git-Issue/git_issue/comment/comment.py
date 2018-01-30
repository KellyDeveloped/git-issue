from gituser import GitUser
from utils import date_utils
from utils.json_utils import JsonConvert
import uuid

@JsonConvert.register
class Comment(object):
    """ Class represents what a comment is. The default date of a comment is the current datetime
        in UTC formatted as ISO. As issue contributors may be situated all across the world,
        using their system time could be dangerous. 
        
        For example, if someone from Bangalore were to make a comment and synchronise with the 
        repository, and then immediately after someone from New York were to then add another
        comment the New York's user would appear to be made before the Bangalore comment due
        to it being in an earlier timezone. """

    def __init__(self, comment:str="", user:GitUser=GitUser(), date=date_utils.get_date_now(),
                uuid=uuid.uuid4().int):
        self.comment = comment
        self.user = user
        self.date = date
        self.uuid = uuid
