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

from issue_web_gui.api.issue.schemas import comment_list_payload, comment_payload, comment_response_fields
from .schemas import IssueSchema, issue_create_fields, issue_fields, GitUserSchema, CommentSchema, comment_fields, \
    to_payload, IssueListSchema, issue_payload, issue_list_payload

import git_issue.issue.handler as handler
from git_issue.issue.issue import Issue, status_indicators
from git_issue.comment import Comment
from git_issue.gituser import GitUser

page_args = {
    'page': fields.Integer(),
    'limit': fields.Integer()
}


class IssueList(object):
    def __init__(self, count: int, issues: Issue):
        self.count = count
        self.issues = issues

@api.route('/issues')
class IssueListAPI(Resource):

    @use_args(page_args)
    @api.doc(description="Retrieves a range of issues based on the given parameters.")
    @api.param('page', 'The page to retrieve. The start position of a page is page * limit.'\
            'Default page is 1.')
    @api.param('limit', 'The amount of comments per page. Default limit of comments is 10.')
    @api.response(200, 'Success', issue_list_payload)
    def get(self, args):
        page = args.get("page", 1)
        limit = args.get("limit", 10)


        issues, count = handler.get_issue_range(page, limit)
        response = IssueList(count, issues)

        result = to_payload(GitUser(), response, IssueListSchema)
        return result.data

    @api.expect(issue_create_fields)
    @api.doc(description="Takes the given issue and creates it in the data layer.")
    @api.param('payload', 'The issue to be created.')
    @api.response(201, 'Created', issue_fields)
    def post(self):
        json = request.get_json()

        issue = Issue()
        issue.summary = json.get("summary")
        issue.description = json.get("description")
        issue.reporter = GitUser(json.get("reporter")) if json.get("reporter") is not None else GitUser()
        issue.assignee = GitUser(json.get("assignee")) if json.get("assignee") is not None else None
        
        issue.subscribers.append(issue.reporter)
        if issue.assignee is not None and issue.assignee not in issue.subscribers:
            issue.subscribers.append(issue.assignee)
        
        created_issue = handler.store_issue(issue, "create", generate_id=True)
        result = to_payload(GitUser(), issue, IssueSchema)

        return result.data, HTTPStatus.CREATED, {'location': f'issues/${created_issue.id}'}


@api.route('/issues/<string:id>')
@api.doc(params={'id': 'The issue ID in question'})
class IssueAPI(Resource):

    @api.doc(description="Retrieves a single issue that matches the given ID")
    @api.response(200, 'Success', issue_payload)
    def get(self, id):
        if (not handler.does_issue_exist(id)):
            abort(HTTPStatus.NOT_FOUND)
        
        issue = handler.get_issue(id)
        result = to_payload(GitUser(), issue, IssueSchema)
        return result.data

    @api.expect(issue_fields)
    @api.doc(description="Takes the given issue and edits it in the data layer. The issue will be created if it does"
                         "not exist")
    @api.param('payload', 'The issue to be edited.')
    @api.response(200, 'Success', issue_fields)
    @api.response(201, 'Created', issue_fields)
    def put(self, id):
        edit_schema = IssueSchema(only=tuple(IssueSchema.issue_fields.keys()))
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

        result = to_payload(GitUser(), issue, IssueSchema)

        return result.data, HTTPStatus.OK


@api.route('/issues/<string:id>/comments')
@api.doc(params={'id': 'The issue ID that owns the comments'})
class CommentListAPI(Resource):

    @use_args(page_args)
    @api.param('page', 'The amount of comments to return. The start position of a page is page * limit.'\
            'Default page is 1.')
    @api.param('limit', 'The amount of comments per page. Default limit of comments is 10.')
    @api.response(200, 'Success', comment_list_payload)
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
    @api.param('payload', 'The comment to be added')
    @api.response(201, 'Created', comment_response_fields)
    def post(self, id):
        if (not handler.does_issue_exist(id)):
            raise BadRequest(f"Issue with id {id} does not exist.")
        
        comment = request.get_json().get("comment")

        if (comment is None):
            raise BadRequest(f"No comment given.")

        comment = Comment(comment)
        created_comment = handler.add_comment(id, comment)
        
        schema = CommentSchema()
        result = schema.dump(comment)

        return result.data, HTTPStatus.CREATED


@api.route('/status-indicators')
class StatusIndicatorsAPI(Resource):

    def get(self):
        return status_indicators