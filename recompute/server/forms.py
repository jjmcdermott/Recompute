import flask_wtf
from wtforms import StringField, SelectField, BooleanField
from wtforms.validators import DataRequired
from recompute.server import boxes as recompute_boxes


class RecomputeForm(flask_wtf.Form):
    name = StringField("name", validators=[DataRequired()])
    github_url = StringField("github_url", validators=[DataRequired()])
    box = SelectField("box", choices=recompute_boxes.BASE_BOXES, validators=[DataRequired()])


class FilterRecomputationsForm(flask_wtf.Form):
    name = StringField("name", validators=[DataRequired()])
    clear = BooleanField('clear')


#
# class EditRecomputationForm(flask_wtf.Form):
#     name = wtfSelectField("name", validators=[wtfDataRequired()])
#

class FilterBoxesForm(flask_wtf.Form):
    language = StringField("language", validators=[DataRequired()])
    clear = BooleanField('clear')
