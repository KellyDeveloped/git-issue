import git
from git import GitCommandError

from git_issue.git_manager import RepoHandler
from git_issue.git_utils.merge_utils import GitMerge, CreateConflictResolver

from git import RemoteProgress

class GitSynchronizer(object):

    def __init__(self):
        self.repo = RepoHandler.obtain_repo()

    def push(self):
        try:
            self.repo.remote().push()
        except GitCommandError as e:
            print("Failed to push to remote issue branch. Refer to the error below for more details")
            print(e.stdout)

    def pull(self, merge_on_failure=False):
        try:
            self.repo.remote().pull()
        except GitCommandError as e:
            merger = GitMerge(self.repo)

            if merge_on_failure and merger.has_conflicts():
                self.merge(merger)
            else:
                print("Failed to push to remote issue branch. Refer to the error below for more details:")
                print(e.stdout)

    def merge(self, merger):
        conflicts = merger.parse_unmerged_conflicts()
        create_resolver: CreateConflictResolver = merger.produce_create_resolver(conflicts)
        create_resolution = create_resolver.generate_resolution()
        create_resolution.resolve()
        divergence_resolver = merger.produce_create_edit_divergence_resolver(conflicts,
                                                                             create_resolution.resolved_issues,
                                                                             create_resolution.tracker)
        divergence_resolution = divergence_resolver.generate_resolution()
        divergence_resolution.resolve()
        comment_resolvers = merger.produce_comment_index_resolvers(conflicts)
        for resolver in comment_resolvers:
            resolution = resolver.generate_resolution()
            resolution.resolve()
        manual_conflicts = merger.filter_manual_conflicts(conflicts)

        if manual_conflicts == []:
            self.repo.git.commit("-m", "merge conflict resolution")
        else:
            print("I wasn't able to resolve all the conflicts. This typically happens when something's been edited "
                  "in both the remote and current repository.")
            print("Here are the files I couldn't resolve:")

            for conflict in manual_conflicts:
                print(f"\t{conflict.path}")
