import git
import os
import shutil
from pathlib import Path
from typing import Callable

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
        #rs = [r for r in repo.remote().refs if r.remote_head == self.ISSUE_BRANCH]
        return True

    def should_create_new_branch(self) -> bool:
        print("Cannot find issue branch. I can create one automatically for you, however "
              "the current working branch will need changed until. The branch will be changed back to the current"
              "branch once the new branch is created.\n\n"
              "The reason for this is that the branch needs to be orphaned - in other words entirely disconnected "
              "from the current head in order to have zero history.\n\n"
              "This warning is due to unforeseen side affects, such as IDE's detecting the changes and possibly losing"
              "any work. If you do not wish for me to create the branch, you can do it yourself with the following"
              "command: git checkout --orphan issue")
        create = input(f"\nConfirm new branch creation (Y/N): ").capitalize()

        while create != "Y" and create != "YES" and create != "N" and create != "NO":
            create = input("\nInvalid input, please try again (Y/N): ").capitalize()

        if create == "Y" or create == "YES":
            return True

        else:
            return False

    def set_up_branch(self):
        self.load_issue_branch()
        self.pull()
        
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
            if not self.should_create_new_branch():
                print("Branch not created. Exiting program.")
                exit()

            curr_branch = repo.head.ref
            repo.git.checkout("--orphan", self.ISSUE_BRANCH)
            repo.git.rm("-r", "--cached", ".")
            # current_head = repo.head.ref
            # new_head = git.Head(repo, f"refs/heads/{self.ISSUE_BRANCH}")
            # repo.head.reference = new_head
            # repo.git.rm("-rf", ".")
            self.commit("created_issue_branch", new_branch=True)
            # repo.head.reference = current_head
            repo.git.checkout("-")

        worktree_path = Path(repo.git_dir).joinpath("worktrees/issue")

        if not os.path.exists(path) and os.path.exists(worktree_path):
            shutil.rmtree(worktree_path)
        elif os.path.exists(path) and not os.path.exists(worktree_path):
            print(f"An issue folder already exists at location {path}.")
            print("This folder is required to create a worktree of the issue branch.")
            print("As this could be a user-created folder, I need confirmation on if I can delete this folder.")
            print("\n\nPlease review the contents before proceeding.")

            proceed = input("\nConfirm deletion (Y/N): ").capitalize()

            while proceed != "Y" and proceed != "YES" and proceed != "N" and proceed != "NO":
                proceed = input("\nInvalid input, please try again (Y/N): ").capitalize()

            if proceed == "Y" or proceed == "YES":
                shutil.rmtree(path)
                print(f"\nDirectory {path} successfully deleted.")

            else:
                print("\nOperation cancelled.")
                print("Please change your configuration to use a new non-conflicting branch name.")
                print("Note that this requires manually migrating branches.")
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
                repo.git.rm("-rf", "--cached", ".")
                self.commit("created_issue_branch", new_branch=True)
                # repo.git.push("-u", "origin", self.ISSUE_BRANCH)
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
            print("Pulling from issue branch.")

            repo.git.pull()

    def add_to_index(self, paths: [str]):
        repo = self.obtain_repo()
        repo.index.add(paths)

    def push(self):
        repo = self.obtain_repo()
        print("Pushing to issue branch")
        repo.remote().push(self.ISSUE_BRANCH)

    def commit(self, cmd, id: str = None, new_branch=False):
        commit_message = f"Action {cmd} performed"

        if id != None:
            commit_message = f"{commit_message} on issue: {id}"

        # print("committing the following files:")
        # for path in paths:
        #    print(f"\t{path}")
        # print("\nwith the commit message: {commit_message}")

        repo = self.obtain_repo()
        if new_branch:
            repo.index.commit(commit_message, parent_commits=None)
        else:
            repo.index.commit(commit_message)

    def commit_and_push(self, cmd, id):
        repo = self.obtain_repo()

        if (not self._is_issue_branch_loaded(repo)):
            return

        self.commit(repo, cmd, id)
        self.push(repo)

    def perform_git_workflow(self,
                             action: Callable[[], object or None],
                             should_push=False,
                             generate_index_paths: Callable[[], list] = None,
                             commit_type: str = None,
                             commit_id: str = None):
        """
            This executes the typical git workflow:
                Pull origin/issue;
                Add issue branch as worktree;
                Perform action with issues;

                If action invokes pushable changes:
                    add changes to index;
                    commit changes;

                Unload issue worktree;

                If should_push:
                    push origin/issue;

                Return action results

            This method uses the strategy pattern as we tell it how to behave
            once the git branch is loaded - it knows its to do something, but
            it doesn't know what. The same goes for generating the index path;
            it knows we need paths but we specify how to get them.
        """
        self.set_up_branch()

        result = action()

        if should_push and generate_index_paths is not None:
            paths = generate_index_paths()
            self.add_to_index(paths)
            self.commit(commit_type, commit_id)

        self.unload_issue_branch()

        if should_push:
            self.push()

        return result

    @staticmethod
    def obtain_repo():
        return git.Repo(os.getcwd(), search_parent_directories=True)
