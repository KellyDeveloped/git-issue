import git
import os
import json
class GitUser(object):
    """description of class"""

    # TODO: Add method to get git user on construction
    def __init__(self, repo=None):
        if repo == None:
            repo = git.Repo(os.getcwd(), search_parent_directories=True)
        
        reader = repo.config_reader()
        self.author = reader.get_value("user", "name")
        self.email = reader.get_value("user", "email")


g = GitUser()
print(json.dumps(g.__dict__))
