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

    def _is_issue_branch_loaded(self, repo):
        git_dir = Path(repo.git_dir)
        worktree_path = git_dir.joinpath(f"worktrees/{self.ISSUE_BRANCH}")
        
        working_dir = Path(repo.working_dir)
        issue_dir = working_dir.joinpath(self.ISSUE_BRANCH)

        worktrees_exist = working_dir.match(f"*/{self.ISSUE_BRANCH}") or Path.exists(issue_dir)
        issue_files_exist = git_dir.match(f"*worktrees/{self.ISSUE_BRANCH}") or Path.exists(worktree_path)
        return worktrees_exist and issue_files_exist

    def _does_repo_have_issue_remote(self, repo):
        rs = [r for r in repo.remote().refs if r.remote_head == self.ISSUE_BRANCH]
        return rs.count == 1

    def load_issue_branch(self):
        repo = self.obtain_repo()

        issue_path = "{}/{}".format(repo.working_dir, self.ISSUE_BRANCH)
        path = os.path.normpath(issue_path)

        if (self._is_issue_branch_loaded(repo)):
            if (Path.cwd() != path):
                os.chdir(path)
            return

        new_branch = False

        if not hasattr(repo.refs, self.ISSUE_BRANCH):
            repo.create_head(self.ISSUE_BRANCH)
            new_branch = True

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
                self.commit(repo, "created_issue_branch")
                repo.git.push("-u", "origin", self.ISSUE_BRANCH)
        else:
            raise git.CommandError("Failed to add a work tree for branch {} at path {}"
                                .format(self.ISSUE_BRANCH, path))

    def unload_issue_branch(self):
        repo = self.obtain_repo()

        if (not self._is_issue_branch_loaded(repo)):
            return

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
        if (self._does_repo_have_issue_remote(repo)):
            print ("Pulling from issue branch.")
            repo.remote().pull(self.ISSUE_BRANCH)

    def add_to_index(self, paths:[str]):
        repo = self.obtain_repo()
        repo.index.add(paths)

    def push(self):
        repo = self.obtain_repo()
        print ("Pushing to issue branch")
        repo.remote().push(self.ISSUE_BRANCH)

    def commit(self, cmd, id:str=None):
        commit_message = f"Action {cmd} performed"

        if id != None:
            commit_message = f"{commit_message} on issue: {id}"

        #print("committing the following files:")
        #for path in paths:
        #    print(f"\t{path}")
        #print("\nwith the commit message: {commit_message}")

        repo = self.obtain_repo()
        repo.index.commit(commit_message)


    def commit_and_push(self, cmd, id):
        repo = self.obtain_repo()

        if (not self._is_issue_branch_loaded(repo)):
            return

        self.commit(repo, cmd, id)
        self.push(repo)
        
    @staticmethod
    def obtain_repo():
        return git.Repo(os.getcwd(), search_parent_directories=True)