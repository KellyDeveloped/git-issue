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

        new_branch = False

        if not hasattr(repo.refs, self.ISSUE_BRANCH):
            repo.create_head(self.ISSUE_BRANCH)
            new_branch = True

        issue_path = "{}/{}".format(repo.working_dir, self.ISSUE_BRANCH)
        path = os.path.normpath(issue_path)
        repo.git.worktree("add", path, self.ISSUE_BRANCH)

        if os.path.exists(path):
            os.chdir(path)

            """ New branch will have all files from master inside it. 
                Obtain a new repo so that it's referencing
                the worktree that we've just added, and remove all the existing files. """
            if new_branch:
                repo = self.obtain_repo()
                repo.git.rm("-rf", ".")
                self._commit(repo, "created_issue_branch")


            return os.getcwd();

        raise git.CommandError("Failed to add a work tree for branch {} at path {}"
                                .format(self.ISSUE_BRANCH, path))

    def unload_issue_branch(self):
        repo = self.obtain_repo()

        # working directory should be that of the /issue branch produced by load_issue_branch
        path = os.path.normpath(repo.working_dir)

        os.chdir("..")
        shutil.rmtree(path)
        
        repo = self.obtain_repo()
        repo.git.worktree("prune")

    def pull(self):
        repo = self.obtain_repo()
        print ("Pulling from issue branch.")
        repo.remote().pull(self.ISSUE_BRANCH)

    def _push(self, repo):
        repo.remote().push(self.ISSUE_BRANCH)

    def _commit(self, repo, cmd, issue=None, path=None):
        index = repo.index

        # Add unstaged files if provided
        if path != None:
            index.add(path)

        commit_message = f"Action {cmd} performed"

        if issue != None:
            commit_message = f"{commit_message} on issue: {issue.id}"

        index.commit(commit_message)


    def commit_and_push(self, cmd, issue, path:[str]):
        repo = self.obtain_repo()
        self._commit(repo, cmd, issue, path)
        self._push(repo)
        
    @staticmethod
    def obtain_repo():
        return git.Repo(os.getcwd(), search_parent_directories=True)