import git
from git import GitCommandError

from git_issue.git_manager import GitManager
from git_issue.git_manager import RepoHandler
from git_issue.git_utils.merge_utils import GitMerge, CreateConflictResolver
from git_issue.issue.tracker import Tracker


class GitSynchronizer(object):

    def __init__(self):
        self.repo = RepoHandler.obtain_repo()

    def push(self):
        try:
            print("Pushing to remote branch.")
            self.repo.git.push()
            print("Successfully pushed to remote branch.")
        except GitCommandError as e:
            print("Failed to push to remote issue branch. Refer to the error below for more details")
            print(e.stderr)

    def pull(self, merge_on_failure=False):
        try:
            print("Pulling from remote branch.")
            self.repo.git.pull()
            print("Successfully pulled from remote branch.")
        except GitCommandError as e:
            merger = GitMerge(self.repo)

            if merge_on_failure and merger.has_conflicts():
                self.merge(merger)
            else:
                print("Failed to pull from remote issue branch. Refer to the error below for more details:")
                print(e.stderr)

    def merge(self, merger):
        print("Beginning merge process")
        conflicts = merger.parse_unmerged_conflicts()
        create_resolver = merger.produce_create_resolver(conflicts)
        create_resolution = create_resolver.generate_resolution()
        create_resolution.resolve()

        tracker = create_resolution.tracker if create_resolution.tracker.issue_count != 0 else Tracker.obtain_tracker()

        divergence_resolver = merger.produce_create_edit_divergence_resolver(conflicts,
                                                                             create_resolution.resolved_issues,
                                                                             tracker)
        divergence_resolution = divergence_resolver.generate_resolution()
        divergence_resolution.resolve()

        comment_resolvers = merger.produce_comment_index_resolvers(conflicts)
        for resolver in comment_resolvers:
            resolution = resolver.generate_resolution()
            resolution.resolve()

        manual_conflicts = merger.filter_manual_conflicts(conflicts)

        if manual_conflicts == []:
            self.repo.git.commit("-m", "merge conflict resolution")
            print("Merge successful. All files have been merged.")
        else:
            print("I wasn't able to resolve all the conflicts. This typically happens when something's been edited "
                  "in both the remote and current repository.")
            print("Here are the files I couldn't resolve:")

            for conflict in manual_conflicts:
                print(f"\t{conflict.path}")

            gm = GitManager()
            if gm.is_worktree():
                print("Exiting program to prevent branch unloading. This would cause loss of resolved conflicts.")
                exit()
