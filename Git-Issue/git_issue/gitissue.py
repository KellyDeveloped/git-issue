#!/usr/bin/env python

import argparse
import issue.handler as issue_handler
from git_manager import GitManager
from issue.issue import Issue
from gituser import GitUser
from comment.comment import Comment

# Arguments start here
parser = argparse.ArgumentParser(prog='git issue')


class DisplayVersion(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        VERSION = '0.0.1'
        print('Software version of Git Issue: {0}'.format(VERSION))


parser.add_argument('--version', help='Displays the version of this program.', action=DisplayVersion, nargs='?')

subparser = parser.add_subparsers()

# Sub-parsers defined here
createParser = subparser.add_parser('create', help='Create a new issue.')
editParser = subparser.add_parser('edit', help='Edit an existing issue.')
commentParser = subparser.add_parser('comment', help='Add a comment an existing issue.')
showParser = subparser.add_parser('show', help="""Show the information for a given issue.
        If no issue is given, a list of issues will be shown as if you called the "list" command.""")
listParser = subparser.add_parser('list', help='List known issues.')
subscribeParser = subparser.add_parser('subscribe', help='Subscribe to an existing issue.')
unsubscribeParser = subparser.add_parser('unsubscribe', help='Unsubscribe from an existing issue.')

pushParser = subparser.add_parser('push', help='Push the issue branch to its remote.')

# status shorthands
openIssueParser = subparser.add_parser('open', help='Sets the status of the given issue to "Open"')
closeIssueParser = subparser.add_parser('close', help='Sets the status of the given issue to "Closed"')
inProgressParser = subparser.add_parser('active', help='Sets the status of the given issue to "In Progress"')

openIssueParser.add_argument("issue", nargs=1)
closeIssueParser.add_argument("issue", nargs=1)
inProgressParser.add_argument("issue", nargs=1)


def confirm_operation(issue, operation):
    print("Operation will result in the following issue:\n")
    issue_handler.display_issue(issue)
    create = input(f"\nConfirm (Y/N): ").capitalize()

    while create != "Y" and create != "YES" and create != "N" and create != "NO":
        create = input("\nInvalid input, please try again (Y/N): ").capitalize()

    if create == "Y" or create == "YES":
        operation()
        print(f"Operation successful.")

    else:
        print("Operation cancelled.")


# Default methods for sub-parsers. These methods will be called when the keyword for the sub-parser is given.
def create(args):
    issue = Issue()
    issue.summary = args.summary
    issue.description = args.description
    issue.assignee = GitUser(email=args.assignee) if args.assignee != None else None
    issue.reporter = GitUser(email=args.reporter)
    issue.subscribers.append(GitUser())

    def operation():
        new_issue = issue_handler.store_issue(issue, "creation", True)
        print(f"ID of newly created issue: {new_issue.id}")

    confirm_operation(issue, operation)


def edit(args):
    if (not issue_handler.does_issue_exist(args.issue)):
        print("Error: Issue does not exist")
        return

    issue = issue_handler.get_issue(args.issue)

    if (issue == None):
        print("There was a problem ")

    print("Issue before editing:")
    issue_handler.display_issue(issue)

    issue.summary = args.summary if args.summary != None else issue.summary
    issue.description = args.description if args.description != None else issue.description
    issue.assignee = GitUser(email=args.assignee) if args.assignee != None else issue.assignee
    issue.reporter = GitUser(email=args.reporter) if args.reporter != None else issue.reporter
    issue.status = args.status if args.status != None else issue.status

    print()
    confirm_operation(issue, lambda: issue_handler.store_issue(issue, "edit"))


def change_status(issue_id, status):
    handler = issue_handler.IssueHandler()

    if not handler.does_issue_exist(issue_id):
        print("Error: Issue does not exist")
        return

    issue = handler.get_issue_from_issue_id(issue_id)
    original_status = issue.status
    issue.status = status
    handler.store_issue(issue, "edit")
    print(f"Status of {issue.id} changed from '{original_status}' to '{issue.status}'")


def comment(args):
    comment = Comment(args.comment)
    issue_handler.add_comment(args.issue, comment)


def show(args):
    if args.issue is not None:
        issue = issue_handler.get_issue(args.issue)

        if issue == None:
            print(f"Issue with ID {args.issue} was not found.")
        else:
            issue_handler.display_issue(issue)
    else:
        list(args)


def list(args):
    handler = issue_handler.IssueHandler()
    issues = issue_handler.get_all_issues()
    for i in issues:
        issue_handler.display_issue(i)
        print()


def push(args):
    gm = GitManager()
    gm.push()


def pull(args):
    gm = GitManager()
    gm.pull()


def subscribe(args):
    print("to be defined")


def unsubscribe(args):
    print("to be defined")


createParser.add_argument('--summary', '-s', help='A few words to identify the issue.', required=True)
createParser.add_argument('--description', '-d', help='A more detailed description of the issue.')
createParser.add_argument('--assignee', '-a', help='The person to assign to this issue')
createParser.add_argument('--reporter', '-r', help='This person will be notified when changes are made to the issue')
createParser.set_defaults(func=create)

editParser.add_argument('--issue', '-i', help='The issue to edit.', required=True)
editParser.add_argument('--summary', '-s', help='A few words to identify the issue.')
editParser.add_argument('--description', '-d', help='A more detailed description of the issue.')
editParser.add_argument('--assignee', '-a', help='The person to assign to this issue')
editParser.add_argument('--reporter', '-r', help='This person will be notified when changes are made to the issue')
editParser.add_argument('--status', help='The current status for this project')
editParser.set_defaults(func=edit)

commentParser.add_argument('--issue', '-i', help='The issue to add a comment to', required=True)
commentParser.add_argument('--comment', '-c', help='The comment to be added to the issue', required=True)
commentParser.set_defaults(func=comment)

showParser.add_argument('--issue', '-i', help='Displays the given issue.')
showParser.set_defaults(func=show)

listParser.set_defaults(func=list)

subscribeParser.add_argument('--issue', '-i', help='The issue to subscribe to.', required=True)
subscribeParser.set_defaults(func=subscribe)

unsubscribeParser.add_argument('--issue', '-i', help='The issue to unsubscribe from.', required=True)
unsubscribeParser.set_defaults(func=unsubscribe)

openIssueParser.set_defaults(func=lambda x: change_status(x.issue[0], "Open"))
closeIssueParser.set_defaults(func=lambda x: change_status(x.issue[0], "Closed"))
inProgressParser.set_defaults(func=lambda x: change_status(x.issue[0], "In Progress"))

args = parser.parse_args()
args.func(args)
# Arguments end here
