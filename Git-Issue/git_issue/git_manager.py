import git
import os
from pathlib import Path
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

        worktree_path = Path(repo.git_dir).joinpath("worktrees/issue")
        
        if not os.path.exists(path) and os.path.exists(worktree_path):
            shutil.rmtree(worktree_path)
        elif os.path.exists(path) and not os.path.exists(worktree_path):
            print (f"An issue folder already exists at location {path}.")
            print ("This folder is required to create a worktree of the issue branch.")
            print ("As this could be a user-created folder, I need confirmation on if I can delete this folder.")
            print ("\n\nPlease review the contents before proceeding.")

            proceed = input("\nConfirm deletion (Y/N): ").capitalize()
    
            while proceed != "Y" and proceed != "YES" and proceed != "N" and proceed != "NO":
                proceed = input("\nInvalid input, please try again (Y/N): ").capitalize()

            if proceed == "Y" or proceed == "YES":
                shutil.rmtree(path)
                print(f"\nDirectory {path} successfully deleted.")

            else:
                print ("\nOperation cancelled.")
                print ("Please change your configuration to use a new non-conflicting branch name.")
                print ("Note that this requires manually migrating branches.")
                exit()
        
        if not os.path.exists(path) and not os.path.exists(worktree_path):
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

            return os.getcwd()

        raise git.CommandError("Failed to add a work tree for branch {} at path {}"
                                .format(self.ISSUE_BRANCH, path))

    def unload_issue_branch(self):
        repo = self.obtain_repo()

        # working directory should be that of the /issue branch produced by load_issue_branch
        working_dir = Path(repo.working_dir)
        if (working_dir.parts[-1] != self.ISSUE_BRANCH):
            issue_path = working_dir.joinpath(self.ISSUE_BRANCH)
            
            if issue_path.exists():
                os.chdir(issue_path)
                repo = self.obtain_repo()
            else:
                return

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