"""
The flask application package.
"""

from flask import Flask, url_for
from issue_web_gui.api import bp

app = Flask(__name__)
app.register_blueprint(bp, url_prefix="/api/v1")

import issue_web_gui.views
import issue_web_gui.api.issue.requests