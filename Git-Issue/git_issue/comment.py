from datetime import datetime
from gituser import GitUser
from json_utils import JsonConvert

@JsonConvert.register
class Comment(object):
    """ Class represents what a comment is. The default date of a comment is the current datetime
        in UTC formatted as ISO. As issue contributors may be situated all across the world,
        using their system time could be dangerous. 
        
        For example, if someone from Bangalore were to make a comment and synchronise with the 
        repository, and then immediately after someone from New York were to then add another
        comment the New York's user would appear to be made before the Bangalore comment due
        to it being in an earlier timezone. """
    def __init__(self):
        self.comment = ""
        self.user = GitUser()
        self.date = datetime.utcnow().isoformat()
