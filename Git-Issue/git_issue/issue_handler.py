import pathlib
from typing import Callable
from pathlib import Path
from git_manager import GitManager
from json_utils import JsonConvert
from tracker import Tracker

def _increment_issue_count():
    tracker = Tracker.obtain_tracker()
    tracker.increment_issue_count()
    tracker.store_tracker()

def _handle_git_flow(action: Callable[[], object or None],
                     should_push=False,
                     generate_index_paths: Callable[[], list]=None,
                     commit_type:str=None,
                     commit_issue_id:str=None
                     ):
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
    gm = GitManager()
    gm.pull()
    gm.load_issue_branch()

    result = action()

    if (should_push and generate_index_paths != None):
        paths = generate_index_paths()
        gm.add_to_index(paths)
        gm.commit(commit_type, commit_issue_id)

    gm.unload_issue_branch()
    
    if (should_push):
        gm.push()

    return result
        
def _generate_issue_folder_path(id):
    return Path.cwd().joinpath(id)

def _generate_issue_file_path(id):
    return Path.cwd().joinpath(f"{_generate_issue_folder_path(id)}/issue.json")

def _generate_issue_comment_path(id):
    return Path.cwd().joinpath(f"{_generate_issue_folder_path(id)}/comment")

def generate_issue_id():
    tracker = Tracker.obtain_tracker()
    return "{}-{}".format(tracker.ISSUE_IDENTIFIER, (tracker.issue_count + 1))

def does_issue_exist(id):
    return _generate_issue_file_path(id).exists()

def get_issue(id):
    try:    
        return _handle_git_flow(lambda : JsonConvert.FromFile(_generate_issue_file_path(id)))
    except IOError(e):
        return None

def get_all_issues():
    path = Path.cwd()
    dirs = [d for d in path.iterdir() if d.is_dir() and d.match("ISSUE-*")]
    issues = [get_issue(i.parts[-1]) for i in dirs]

    return issues

def store_issue(issue, cmd):
    file_path = _generate_issue_file_path(issue.id)
    gen_paths = lambda : file_path

    def action():
        path = gen_paths()
        JsonConvert.ToFile(issue, path)
        _increment_issue_count()
        return [str(path)]

    _handle_git_flow(action, True, gen_paths, cmd, issue.id)

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
