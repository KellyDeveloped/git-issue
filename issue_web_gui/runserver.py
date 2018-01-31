"""
This script runs the issue_web_gui application using a development server.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.joinpath("Git-Issue/git_issue")))
print (sys.path)
from os import environ
from issue_web_gui import app


if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
