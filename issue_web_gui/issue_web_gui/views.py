"""
Routes and views for the flask application.
"""

import issue_handler as handler
from issue import Issue
from gituser import GitUser
from datetime import datetime
from flask import render_template, request
from issue_web_gui import app
from .forms import CreateForm, EditForm


@app.route('/')
@app.route('/issue/all')
def all_issues():
    issues = handler.get_all_issues()
    print (issues)
    return render_template(
        'all_issues.html',
        issues=issues
        )

@app.route('/issue/create', methods=["GET", "POST"])
def create_issue_form():
    form = CreateForm(request.form)

    if form.validate():
        issue = Issue()
        issue.summary = form.summary.data
        issue.description = form.description.data
        issue.reporter = GitUser(form.reporter_email.data)
        issue.assignee = GitUser(form.assignee_email.data) if form.assignee_email.data != "" else None
        issue = handler.store_issue(issue, "edit")
        
        return render_template("single_issue.html", issue=issue)

    return render_template("create_issue.html", form=form)

@app.route('/issue/edit/<id>', methods=["GET", "POST"])
def edit_issue_form(id):
    form = EditForm(request.form)

    if form.validate():
        issue = Issue()
        issue.id = id
        issue.summary = form.summary.data
        issue.description = form.description.data
        issue.reporter = GitUser(form.reporter_email.data) if form.reporter_email.data != "" else None
        issue.assignee = GitUser(form.assignee_email.data) if form.assignee_email.data != "" else None
        issue.status = form.status.data
        
        user = GitUser()
        if (form.subscribed.data):
            matches = [sub for sub in issue.subscribers if sub.email == user.email]

            if (len(matches) == 0):
                issue.subscribers.append(user)
        else:
            issue.subscribers = [sub for sub in issue.subscribers if sub.email != user.email()]

        issue = handler.store_issue(issue, "edit")
        
        return render_template("single_issue.html", issue=issue)

    issue = handler.get_issue(id)

    if issue is None:
        return render_template("error_page.html", error_msg=f"Issue {id} not found.")

    form.summary.data = issue.summary
    form.description.data = issue.description
    form.status.data = issue.status
    form.subscribed.data = False # This needs changed to check if git user is subscribed
    
    if (issue.reporter is not None):
        form.reporter_email.data = issue.reporter.email

    if (issue.assignee is not None):
        form.assignee_email.data = issue.assignee.email

    form = EditForm(obj=issue)

    return render_template("edit_issue.html", form=form, issue=issue)

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

