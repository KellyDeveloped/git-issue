import git
import os
import shutil

class GitManager(object):
    """ This class behaves as an interface between the front of the program and GIT.
        This is an attempt to keep most of the GIT interfacing in one manageable place.
        It's purpose is to also keep the front end cli separate from any backend interactions. """
    
    ISSUE_BRANCH = "issue"
    ORIGINAL_BRANCH = os.getcwd()

    def load_issue_branch(self):
        repo = self.obtain_repo()

        issue_path = "{}/{}".format(repo.working_dir, self.ISSUE_BRANCH)
        path = os.path.normpath(issue_path)
        repo.git.worktree("add", path, self.ISSUE_BRANCH)
        
        if os.path.exists(path):
            os.chdir(path)
            return os.getcwd();

        raise git.CheckoutError("Failed to add a work tree for branch {} at path {}"
                                .format(self.ISSUE_BRANCH, path))

    def unload_issue_branch(self):
        repo = self.obtain_repo()

        # working directory should be that of the /issue branch produced by load_issue_branch
        path = os.path.normpath(repo.working_dir)

        os.chdir("..")
        shutil.rmtree(path)
        
        repo = self.obtain_repo()
        repo.git.worktree("prune")

    @staticmethod
    def obtain_repo():
        return git.Repo(os.getcwd(), search_parent_directories=True)
