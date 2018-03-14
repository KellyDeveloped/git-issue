from marshmallow import Schema, fields, post_load
from flask_restplus import fields as rfields
from issue_web_gui.api import api
from git_issue.issue import Issue

from git_issue.gituser import GitUser

class GitUserSchema(Schema):
    user = fields.Str()
    email = fields.Email()

    user_fields = {
                'user': rfields.String,
                'email': rfields.String(description='Email of a git-author on this repository.',
                                        required=True)
            }

git_user_fields = api.model('User', GitUserSchema.user_fields)

class IssueSchema(Schema):

    id = fields.Str(required=True)
    date = fields.Str(allow_none=True)
    summary = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    status = fields.Str(allow_none=True)
    assignee = fields.Nested(GitUserSchema, allow_none=True)
    reporter = fields.Nested(GitUserSchema, allow_none=True)
    subscribers = fields.Nested(GitUserSchema, many=True)

    edit_fields = {
            'id' : rfields.String,
            'summary': rfields.String(required=True),
            'description': rfields.String,
            'status': rfields.String(required=True),
            'assignee': rfields.Nested(git_user_fields),
            'reporter': rfields.Nested(git_user_fields),
            'subscribers': rfields.List(rfields.Nested(git_user_fields)),
        }

    create_fields = {
            'summary': rfields.String(required=True),
            'description': rfields.String,
            'assignee': rfields.Nested(git_user_fields),
            'reporter': rfields.Nested(git_user_fields),
        }

    @post_load
    def make_issue(self, data):
        return Issue(**data)

issue_create_fields = api.model('Create Issue', IssueSchema.create_fields)
issue_edit_fields = api.model('Edit Issue', IssueSchema.edit_fields) 

class IssueListSchema(Schema):

    count = fields.Int()
    issues = fields.Nested(IssueSchema, many=True)

class CommentSchema(Schema):
    comment = fields.Str()
    user = fields.Nested(GitUserSchema)
    date = fields.Str()
    uuid = fields.Str()

    create_fields = {
            'comment': rfields.String
        }

comment_fields = api.model('Comment', CommentSchema.create_fields)

class Payload(object):

    def __init__(self, user: GitUser, payload):
        self.user = user
        self.payload = payload

def to_payload(current_user, obj, schema_type: Schema, many=False):
    class PayloadSchema(Schema):
        user = fields.Nested(GitUserSchema)
        payload = fields.Nested(schema_type, many=many)

    ps = PayloadSchema()
    #{ "user": gu, "payload": obj}
    return ps.dump(Payload(current_user, obj))