import git
from git import GitCommandError

from git_issue.git_manager import RepoHandler
from git_issue.git_utils.merge_utils import GitMerge
from git_issue.comment import Comment

class GitSynchroniser(object):

    def __init__(self):
        self.repo = RepoHandler.obtain_repo()

    def push(self):
        try:
            self.repo.remote()
        except GitCommandError as e:
            print("Failed to push to remote issue branch. Refer to the error below for more details")
            print(e.stdout)

    def pull(self, merge_on_failure = False):
        try:
            self.repo.remote()
        except GitCommandError as e:
            print("Failed to push to remote issue branch. Refer to the error below for more details")
            print(e.stdout)