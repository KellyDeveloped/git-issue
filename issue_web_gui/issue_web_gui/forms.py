from wtforms import Form, StringField, BooleanField, validators

class CreateForm(Form):
    summary = StringField("Summary", [validators.DataRequired()])
    description = StringField("Description")
    assignee_email = StringField("Assignee")
    reporter_email = StringField("Reporter")

class EditForm(Form):
    status_list = ["open", "closed"]

    summary = StringField("Summary", [validators.DataRequired()])
    description = StringField("Description")
    assignee_email = StringField("Assignee")
    reporter_email = StringField("Reporter")
    status = StringField("Status", [validators.AnyOf(status_list)])
    subscribed = BooleanField("Subscribed", [validators.DataRequired()])