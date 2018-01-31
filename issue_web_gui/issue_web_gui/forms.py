from wtforms import Form, StringField, BooleanField, validators

class CreateForm(Form):
    summary = StringField("Summary", [validators.DataRequired()])
    description = StringField("Description")
    assignee = StringField("Assignee")
    reporter = StringField("Reporter")

class EditForm(Form):
    status_list = ["open", "closed"]

    summary = StringField("Summary", [validators.DataRequired()])
    description = StringField("Description")
    assignee = StringField("Assignee")
    reporter = StringField("Reporter")
    status = StringField("Status", [validators.AnyOf(status_list)])
    subscribed = BooleanField("Subscribed", [validators.DataRequired()])