#!/usr/bin/env python

import argparse

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

# Default methods for sub-parsers. These methods will be called when the keyword for the sub-parser is given.
def create(args):
    print("to be defined")

def edit(args):
    print("to be defined")

def comment(args):
    print("to be defined")

def show(args):
    print("to be defined")

def list(args):
    print("to be defined")

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


subscribeParser.add_argument('--issue', '-i', help='The issue to subscribe to.')
subscribeParser.set_defaults(func=subscribe)

unsubscribeParser.add_argument('--issue', '-i', help='The issue to unsubscribe from.')
unsubscribeParser.set_defaults(func=unsubscribe)

args = parser.parse_args()
args.func(args)
# Arguments end here