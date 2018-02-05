"""
Routes and views for the flask application.
"""
from flask_restplus import Resource
from issue_web_gui.api import api
from flask import render_template, request
from flask_restplus_marshmallow import Schema
from marshmallow import pprint
from webargs import fields
from webargs.flaskparser import use_args
from werkzeug.exceptions import BadRequest

from .schemas import IssueSchema, issue_create_fields, issue_edit_fields, GitUserSchema, CommentSchema, comment_fields

import issue_handler as handler
from issue import Issue
from comment import Comment
from gituser import GitUser
from datetime import datetime


@api.route('/issues')
class IssueListAPI(Resource):
    def get(self):
        issues = handler.get_all_issues()
        schema = IssueSchema()
        result = schema.dump(issues, many=True)
        return result.data

    @api.expect(issue_create_fields)
    def post(self):
        json = request.get_json()

        issue = Issue()
        issue.summary = json.get("summary")
        issue.description = json.get("description")
        issue.reporter = GitUser(json.get("reporter")) if json.get("reporter") is not None else GitUser()
        issue.assignee = GitUser(json.get("assignee")) if json.get("assignee") is not None else None
        
        issue.subscribers.append(issue.reporter)
        if issue.assignee is not None:
            issue.subscribers.append(issue.assignee)
        
        created_issue = handler.store_issue(issue, "create", generate_id=True)
        schema = IssueSchema()
        result = schema.dump(created_issue)

        return result.data


@api.route('/issues/<string:id>')
class IssueAPI(Resource):
    def get(self, id):
        if (not handler.does_issue_exist(id)):
            raise BadRequest(f"Issue with id {id} does not exist.")
        
        issue = handler.get_issue(id)
        schema = IssueSchema()
        result = schema.dump(issue)
        return result.data

    @api.expect(issue_edit_fields)
    def put(self, id):
        if (not handler.does_issue_exist(id)):
            raise BadRequest(f"Issue with id {id} does not exist.")
        
        schema = IssueSchema(only=tuple(IssueSchema.edit_fields.keys()))
        result = schema.load(request.get_json())
        return result.data
        


page_args = {
    'page': fields.Integer(),
    'limit': fields.Integer()
}


@api.route('/issues/<string:id>/comments')
class CommentListAPI(Resource):

    @use_args(page_args)
    @api.param('page', 'Which server to collect data from when in multi-agent mode')
    @api.param('limit', 'Which server to collect data from when in multi-agent mode')
    def get(self, args, id):
        if (not handler.does_issue_exist(id)):
            raise BadRequest(f"Issue with id {id} does not exist.")
        
        page = args.get("page", 1)
        limit = args.get("limit", 10)
        
        # Each page is limit amount of comments, therefore start_pos
        # is the limit of comments per page, times by the page number
        start_pos = limit * (page - 1)

        comments = handler.get_comment_range(id, limit, start_pos)
        schema = CommentSchema()
        result = schema.dump(comments, many=True)

        return result.data

    @api.expect(comment_fields)
    def post(self, id):
        if (not handler.does_issue_exist(id)):
            raise BadRequest(f"Issue with id {id} does not exist.")
        
        comment = request.get_json().get("comment")

        if (comment is None):
            raise BadRequest(f"No comment given.")

        created_comment = handler.add_comment(id, Comment(comment))
        
        schema = CommentSchema()
        result = schema.dump(comment)

        return result.data