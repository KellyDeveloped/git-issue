from pathlib import Path
from git_manager import GitManager
from utils.json_utils import JsonConvert
from tracker import Tracker
from comment.handler import CommentHandler


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

        JsonConvert.ToFile(issue, _generate_issue_file_path(issue.id))
        _increment_issue_count()
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
