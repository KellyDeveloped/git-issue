"""
Routes and views for the flask application.
"""
from flask_restplus import Resource
from issue_web_gui.api import api
from flask import render_template, request, abort
from flask_restplus_marshmallow import Schema
from marshmallow import pprint
from webargs import fields
from webargs.flaskparser import use_args
from werkzeug.exceptions import BadRequest

from http import HTTPStatus
import hashlib

from .schemas import IssueSchema, issue_create_fields, issue_edit_fields, GitUserSchema, CommentSchema, comment_fields, to_payload

import issue_handler as handler
from issue import Issue, status_indicators
from comment import Comment
from gituser import GitUser
from datetime import datetime


@api.route('/issues')
class IssueListAPI(Resource):
    def get(self):
        issues = handler.get_all_issues()
        result = to_payload(GitUser(), issues, IssueSchema, many=True)
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
        result = to_payload(GitUser(), issues, IssueSchema)

        return result.data, 201, {'location': f'issues/${create_issue.id}'}


@api.route('/issues/<string:id>')
class IssueAPI(Resource):
    def get(self, id):
        if (not handler.does_issue_exist(id)):
            abort(HTTPStatus.NOT_FOUND)
        
        issue = handler.get_issue(id)
        result = to_payload(GitUser(), issue, IssueSchema)
        return result.data

    @api.expect(issue_edit_fields)
    def put(self, id):
        edit_schema = IssueSchema(only=tuple(IssueSchema.edit_fields.keys()))
        regular_schema = IssueSchema()
        parsed_data = edit_schema.load(request.get_json())

        if (len(parsed_data.errors.items()) > 0):
            return f"Errors encountered with the request: {parsed_data.errors}", 416

        updated_issue = parsed_data.data

        issue = None
        httpStatus: HTTPStatus = None
        headers = {}

        if (not handler.does_issue_exist(id)):
            issue = handler.store_issue(updated_issue, "create", True)

            hash = hashlib.sha256(b"{regular_schema.dump(issue).data}").hexdigest()
            print (f"Hash: {hash}")
            headers["ETag"] = hash
            httpStatus = HTTPStatus.CREATED

        else:
            current_issue = handler.get_issue(id)

            if (updated_issue.id != id):
                return "Given issue ID does not match url", 416

            updated_issue.date = current_issue.date # Ensure date NEVER changes
            issue = handler.store_issue(updated_issue, "edit")

        return regular_schema.dump(issue), HTTPStatus.OK
        


page_args = {
    'page': fields.Integer(),
    'limit': fields.Integer()
}


@api.route('/issues/<string:id>/comments')
class CommentListAPI(Resource):

    @use_args(page_args)
    @api.param('page', 'The amount of comments to return. The start position of a page is page * limit.'\
            'Default page is 1.')
    @api.param('limit', 'The amount of comments per page. Default limit of comments is 10.')
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

@api.route('/status-indicators')
class StatusIndicatorsAPI(Resource):

    def get(self):
        return status_indicators