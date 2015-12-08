import wtforms_tornado
from wtforms import StringField, SelectField, BooleanField, IntegerField, TextAreaField
from wtforms.validators import DataRequired

import boxes


class RecomputeForm(wtforms_tornado.Form):
    recomputation = StringField("recomputation", validators=[DataRequired()])
    github_url = StringField("github_url", validators=[DataRequired()])
    box = SelectField("box", choices=boxes.BASE_BOXES, validators=[DataRequired()])


class EditRecomputationForm(wtforms_tornado.Form):
    recomputation = StringField("recomputation", validators=[DataRequired()])
    github_url = StringField("github_url", validators=[DataRequired()])
    description = StringField("description", validators=[DataRequired()])

class RequestDOIForm(wtforms_tornado.Form):
    doi = StringField("doi", validators=[DataRequired()])
    title = StringField("title", validators=[DataRequired()])
    creator = StringField("creator", validators=[DataRequired()])
    publisher = StringField("publisher", validators=[DataRequired()])
    publicationyear = IntegerField("publicationyear", validators=[DataRequired()])
    metadata = TextAreaField("metadata", validators=[DataRequired()])

class FilterRecomputationsForm(wtforms_tornado.Form):
    name = StringField("name", validators=[DataRequired()])
    clear = BooleanField('clear')
