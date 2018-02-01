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

    BRANCH_NOT_DETECTED_MSG = "Cannot find issue branch. I can create one automatically for you, however "\
              "the current working branch will need changed until. The branch will be changed back to the current"\
              "branch once the new branch is created.\n\n"\
              "The reason for this is that the branch needs to be orphaned - in other words entirely disconnected "\
              "from the current head in order to have zero history.\n\n"\
              "This warning is due to unforeseen side affects, such as IDE's detecting the changes and possibly losing"\
              "any work. If you do not wish for me to create the branch, you can do it yourself with the following"\
              "command: git checkout --orphan issue"\

    DIRTY_REPO_MSG = "Current branch is considered dirty and no issue branch has been detected and must be made.\n"\
                  "The process of creating the issue branch may result in loss of work if the branch is dirty.\n"\
                  "Please try again when the branch is in a clean state. Program will now terminate."\

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

    def get_choice_from_user(self, confirm_msg) -> bool:
        create = input(confirm_msg).capitalize()

        while create != "Y" and create != "YES" and create != "N" and create != "NO":
            create = input("\nInvalid input, please try again (Y/N): ").capitalize()

        # If false they said no
        return create == "Y" or create == "YES"

    def set_up_branch(self):
        self.load_issue_branch()
        self.pull()

    def _create_new_issue_branch(self, repo):
        if repo.is_dirty():
            print(self.DIRTY_REPO_MSG)
            exit()

        print(self.BRANCH_NOT_DETECTED_MSG)
        if not self.get_choice_from_user("\nConfirm new branch creation (Y/N): "):
            print("Branch not created. Exiting program.")
            exit()

        curr_branch = repo.head.ref
        repo.git.checkout("--orphan", self.ISSUE_BRANCH)
        repo.git.rm("-rf", "--cached", ".")

        self.commit("created_issue_branch", new_branch=True)
        repo.git.push("-u", "origin", self.ISSUE_BRANCH)

        curr_branch.checkout(force=True)

        
    def load_issue_branch(self):
        repo = self.obtain_repo()

        issue_path = "{}/{}".format(repo.working_dir, self.ISSUE_BRANCH)
        path = os.path.normpath(issue_path)

        if (self._is_issue_branch_loaded(repo)):
            if (Path.cwd() != path):
                os.chdir(path)
            return

        has_remote = len(repo.refs) > 0 and hasattr(repo.remote().refs, self.ISSUE_BRANCH)
        has_local_branch = hasattr(repo.refs, self.ISSUE_BRANCH)
        if not has_local_branch and not has_remote:
            self._create_new_issue_branch(repo)

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
            if has_remote and not has_local_branch:
                repo.git.branch("-f", self.ISSUE_BRANCH, f"origin/{self.ISSUE_BRANCH}")

            repo.git.worktree("add", path, self.ISSUE_BRANCH)

        if os.path.exists(path):
            os.chdir(path)

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
        print("Pulling from issue branch.")
        try:
            repo.git.pull("origin", self.ISSUE_BRANCH)
        except git.exc.GitCommandError as e:
            print("Failed to pull from issue branch. See error below.")
            print(e)            

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
