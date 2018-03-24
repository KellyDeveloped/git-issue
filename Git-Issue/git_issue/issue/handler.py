from pathlib import Path
from git_issue.git_manager import GitManager
from git_issue.issue.issue import Issue
from git_issue.utils.json_utils import JsonConvert
from git_issue.issue.tracker import Tracker
from git_issue.comment.handler import CommentHandler


class IssueHandler(object):
    
    def __init__(self, tracker=None):
        self.tracker = tracker if tracker is not None else Tracker.obtain_tracker()

    def generate_issue_id(self, count: int = None):
        num = self.tracker.issue_count + 1 if count is None else count
        return "{}-{}".format(self.tracker.ISSUE_IDENTIFIER, num)

    def next_issue_id(self, issue_id: str) -> str:
        num = int(issue_id.replace(f"{self.tracker.ISSUE_IDENTIFIER}-", "")) + 1
        return self.generate_issue_id(num)

    @staticmethod
    def _generate_issue_folder_path(id):
        dir = Path.cwd()

        # if GitManager.is_worktree():
        #     dir = dir.joinpath("issue")

        return dir.joinpath(id)

    def _generate_issue_file_path(self, id):
        return Path.cwd().joinpath(f"{self._generate_issue_folder_path(id)}/issue.json")

    def get_issue_path(self, issue: Issue):
        return self._generate_issue_file_path(issue.id)

    def store_issue(self, issue, cmd, generate_id=False):
        def gen_paths():
            return [str(self._generate_issue_file_path(issue.id))]
    
        def action():
            if generate_id:
                issue.id = self.generate_issue_id()
                self.tracker.increment_issue_count()

            JsonConvert.ToFile(issue, self._generate_issue_file_path(issue.id))
            self.tracker.track_or_update_uuid(issue.uuid, issue.id)

            return issue

        gm = GitManager()
        return gm.perform_git_workflow(action, True, gen_paths, cmd, issue.id)

    def get_issue_from_uuid(self, uuid):
        id = self.tracker.get_issue_from_uuid(uuid)
        return self.get_issue_from_issue_id(id)

    def get_issue_from_issue_id(self, id):
        gm = GitManager()
        is_loaded = gm.is_inside_branch()

        if not is_loaded:
            gm.load_issue_branch()

        try:
            file = JsonConvert.FromFile(_generate_issue_file_path(id))
        except FileNotFoundError:
            return None

        if not is_loaded:
            gm.unload_issue_branch()

        return file

    def display_issue(issue, with_comments=False):
        print (f"Issue ID:\t{issue.id}")
        print (f"Summary:\t{issue.summary}")
        print (f"Description:\t{issue.description}")
    
        if with_comments:
            print ("Comments:")
            for c in get_comments:
                print (f"\tUser: {c.user}\tTimestamp:{c.date}")
                print (f'\t"{c.comment}"')

        print (f"Status:\t\t{issue.status}")
    
        if issue.assignee != None:
            print (f"Assignee:\t{issue.assignee.user}, {issue.assignee.email}")
        else:
            print ("Assignee:\tUnassigned")

        if issue.reporter != None:
            print (f"Reporter:\t{issue.reporter.user}, {issue.reporter.email}")
        else:
            print ("Reporter:\tUnassigned")

        print ("Subscribers:")
        for s in issue.subscribers:
            print (f"\t{s.user}, {s.email}")

    def does_issue_exist(self, id: str):
        gm = GitManager()

        is_loaded = gm.is_inside_branch()
        if not is_loaded:
            gm.load_issue_branch()

        exists = _generate_issue_file_path(id).exists()

        if not is_loaded:
            gm.unload_issue_branch()

        return exists

    def get_issue_range(page: int = 1, limit: int = 10):
        gm = GitManager()

        def action():
            start_pos = (page - 1) * limit
            end = start_pos + limit

            path = Path.cwd()
            dirs = [d for d in path.iterdir() if d.is_dir() and d.match("ISSUE-*")]
            range = dirs[start_pos: end]
            return [JsonConvert.FromFile(_generate_issue_file_path(i.parts[-1])) for i in range], len(dirs)

        return gm.perform_git_workflow(action)



def _increment_issue_count():
    tracker = Tracker.obtain_tracker()
    tracker.increment_issue_count()
    tracker.store_tracker()


def _generate_issue_folder_path(id):
    dir = Path.cwd()

    if dir.parts[-1] != "issue":
        dir = dir.joinpath("issue")

    return dir.joinpath(id)


def _generate_issue_file_path(id):
    return Path.cwd().joinpath(f"{_generate_issue_folder_path(id)}/issue.json")


def generate_issue_id():
    tracker = Tracker.obtain_tracker()
    return "{}-{}".format(tracker.ISSUE_IDENTIFIER, (tracker.issue_count + 1))


def does_issue_exist(id):
    gm = GitManager()
    return gm.perform_git_workflow(lambda : _generate_issue_file_path(id).exists())


def get_issue(id):
    gm = GitManager()
    try:    
        return gm.perform_git_workflow(lambda: JsonConvert.FromFile(_generate_issue_file_path(id)))
    except IOError:
        return None


def get_all_issues():
    gm = GitManager()

    def action():
        path = Path.cwd()
        dirs = [d for d in path.iterdir() if d.is_dir() and d.match("ISSUE-*")]
        return [JsonConvert.FromFile(_generate_issue_file_path(i.parts[-1])) for i in dirs]

    return gm.perform_git_workflow(action)

def store_issue(issue, cmd, generate_id=False):
    gen_paths = lambda : [str(_generate_issue_file_path(issue.id))]
    
    def action():
        if (generate_id):
            issue.id = generate_issue_id()
            _increment_issue_count()

        JsonConvert.ToFile(issue, _generate_issue_file_path(issue.id))
        tracker = Tracker.obtain_tracker()
        tracker.track_or_update_uuid(issue.uuid, issue.id)
        tracker.store_tracker()
        return issue

    gm = GitManager()
    return gm.perform_git_workflow(action, True, gen_paths, cmd, issue.id)


def add_comment(issue_id, comment):
    handler = CommentHandler(_generate_issue_folder_path(issue_id), issue_id)
    return handler.add_comment(comment)


def get_comment_range(issue_id, range: int, start_pos: int = 0):
    gm = GitManager()

    def action():
        handler = CommentHandler(_generate_issue_folder_path(issue_id), issue_id)
        return handler.get_comment_range(range, start_pos)

    return gm.perform_git_workflow(action)



def display_issue(issue, with_comments=False):
    print (f"Issue ID:\t{issue.id}")
    print (f"Summary:\t{issue.summary}")
    print (f"Description:\t{issue.description}")
    
    if with_comments:
        print ("Comments:")
        for c in get_comments:
            print (f"\tUser: {c.user}\tTimestamp:{c.date}")
            print (f'\t"{c.comment}"')

    print (f"Status:\t\t{issue.status}")
    
    if issue.assignee != None:
        print (f"Assignee:\t{issue.assignee.user}, {issue.assignee.email}")
    else:
        print ("Assignee:\tUnassigned")

    if issue.reporter != None:
        print (f"Reporter:\t{issue.reporter.user}, {issue.reporter.email}")
    else:
        print ("Reporter:\tUnassigned")

    print ("Subscribers:")
    for s in issue.subscribers:
        print (f"\t{s.user}, {s.email}")
