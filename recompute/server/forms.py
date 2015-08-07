import flask_wtf
from wtforms import StringField as wtfStringField, SelectField as wtfSelectField, BooleanField as wtfBooleanField
from wtforms.validators import DataRequired as wtfDataRequired
from . import consts


class RecomputeForm(flask_wtf.Form):
    name = wtfStringField("name", validators=[wtfDataRequired()])
    github_url = wtfStringField("github_url", validators=[wtfDataRequired()])
    box = wtfSelectField("box", choices=consts.RECOMPUTE_BOXES, validators=[wtfDataRequired()])


class FilterRecomputationsForm(flask_wtf.Form):
    name = wtfStringField("name", validators=[wtfDataRequired()])
    clear = wtfBooleanField('clear')

#
# class EditRecomputationForm(flask_wtf.Form):
#     name = wtfSelectField("name", validators=[wtfDataRequired()])
#

class FilterBoxesForm(flask_wtf.Form):
    language = wtfStringField("language", validators=[wtfDataRequired()])
    clear = wtfBooleanField('clear')
