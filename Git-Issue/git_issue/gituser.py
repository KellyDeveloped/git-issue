from git_issue.git_manager import GitManager
from git_issue.utils.json_utils import JsonConvert
import os

@JsonConvert.register
class GitUser(object):
    """description of class"""

    def __init__(self, user=None, email=None):
        if (email == None):
            self._get_current_user()

        # If user is not provided, try look it up based on email
        elif (email != None and user == None):
            contributor = self.from_email(email)
            
            self.user = contributor.user if contributor != None and contributor.user != None else ""
            self.email = email

        else:
            self.user = user
            self.email = email

    def _get_current_user(self, repo=None):
        repo = GitManager.obtain_repo()

        reader = repo.config_reader()
        self.user = reader.get_value("user", "name")
        self.email = reader.get_value("user", "email")

    @staticmethod
    def from_email(email):
        repo = GitManager.obtain_repo()
        
        #repo.git.shortlog(se)...

        """ To get all contributors we need to query git's CLI directly and
            analyse the shortlog. The command "git shortlog -se" will give all
            contributors names and email addresses in the format of:
            1\tUser <email>\n - and repeats like this until the end."""
        shortlog = repo.git.shortlog("-se")

        for line in shortlog.split("\n"):
            str = line.split("\t")[1]
            temp = str.split(" <")
            if (temp[1].replace(">", "") == email):
                return GitUser(temp[0], email)

        return None

    def __eq__(self, o: object) -> bool:
        if type(o) is not GitUser:
            return False

        o: GitUser = o

        return self.email == o.email

