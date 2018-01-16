import os
from jsonutils import JsonConvert
from tracker import Tracker

def _increment_issue_count():
    tracker = Tracker.obtain_tracker()
    tracker.increment_issue_count()
    tracker.store_tracker()

def generate_issue_id():
    tracker = Tracker.obtain_tracker()
    return "{}-{}".format(tracker.ISSUE_IDENTIFIER, (tracker.issue_count + 1))

def does_issue_exist(id):
    raise NotImplementedError

def get_issue(id):
    raise NotImplementedError

def get_all_issues():
    raise NotImplementedError

def store_issue(issue):
    raw_path = os.getcwd() + "/{}.json".format(issue.id)
    normalised_path = os.path.normpath(raw_path)
    JsonConvert.ToFile(issue, normalised_path)
    _increment_issue_count()

def display_issue(issue):
    print ("Issue ID:\t{}".format(issue.id))
    print ("Summary:\t{}".format(issue.summary))
    print ("Description:\t{}".format(issue.description))
    
    print ("Comments:")
    for c in issue.comments:
        print ("\tUser: {}\tTimestamp:{}".format(c.user, c.date))
        print ('\t"{}"'.format(c.comment))

    print ("Status:\t{}".format(issue.status))
    print ("Assignee:\t{}, {}".format(issue.assignee.user, issue.assignee.email))
    print ("Reporter:\t{}, {}".format(issue.reporter.user, issue.reporter.email))
    
    print ("Subscribers:")
    for s in issue.subscribers:
        print ("\t{}, {}".format(issue.assignee.user, issue.assignee.email))
