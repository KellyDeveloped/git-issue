from marshmallow import Schema, fields, post_load
from flask_restplus import fields as rfields
from issue_web_gui.api import api
from issue import Issue

class GitUserSchema(Schema):
    user = fields.Str()
    email = fields.Email(required=True)

    user_fields = {
                'user': rfields.String,
                'email': rfields.String(description='Email of a git-author on this repository.',
                                        required=True)
            }

git_user_fields = api.model('User', GitUserSchema.user_fields)

class IssueSchema(Schema):

    id = fields.Str(required=True)
    date = fields.Str()
    summary = fields.Str(required=True)
    description = fields.Str()
    status = fields.Str()
    assignee = fields.Nested(GitUserSchema)
    reporter = fields.Nested(GitUserSchema)
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

class CommentSchema(Schema):
    comment = fields.Str()
    user = fields.Nested(GitUserSchema)
    date = fields.Str()
    uuid = fields.Str()

    create_fields = {
            'comment': rfields.String
        }

comment_fields = api.model('Comment', CommentSchema.create_fields)