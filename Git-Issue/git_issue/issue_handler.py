import pathlib
from pathlib import Path
from git_manager import GitManager
from json_utils import JsonConvert
from tracker import Tracker

def _increment_issue_count():
    tracker = Tracker.obtain_tracker()
    tracker.increment_issue_count()
    tracker.store_tracker()

def _generate_issue_path(id):
    return Path.cwd().joinpath(f"{id}/issue.json")

def generate_issue_id():
    tracker = Tracker.obtain_tracker()
    return "{}-{}".format(tracker.ISSUE_IDENTIFIER, (tracker.issue_count + 1))

def does_issue_exist(id):
    return _generate_issue_path(id).exists()

def get_issue(id):
    try:
        gm = GitManager()
        gm.load_issue_branch()
        gm.pull()

        issue = JsonConvert.FromFile(_generate_issue_path(id))

        gm.unload_issue_branch()
        return issue
    except IOError(e):
        return None

def get_all_issues():
    gm = GitManager()
    gm.pull()
    gm.load_issue_branch()

    path = Path.cwd()
    dirs = [d for d in path.iterdir() if d.is_dir() and d.match("ISSUE-*")]
    issues = [get_issue(i.parts[-1]) for i in dirs]

    gm.unload_issue_branch()
    return issues

def store_issue(issue, cmd):
    gm = GitManager()
    gm.pull()
    gm.load_issue_branch()

    path = _generate_issue_path(issue.id)
    JsonConvert.ToFile(issue, path)
    _increment_issue_count()

    gm.add_to_index([str(path)])

    gm.commit(cmd, issue.id)
    gm.unload_issue_branch()
    gm.push()

def display_issue(issue):
    print (f"Issue ID:\t{issue.id}")
    print (f"Summary:\t{issue.summary}")
    print (f"Description:\t{issue.description}")
    
    print ("Comments:")
    for c in issue.comments:
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
