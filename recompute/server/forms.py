from flask_wtf import Form
from wtforms import StringField, BooleanField, SelectField, TextAreaField
from wtforms.validators import Required, Length

class FilterSoftwareForm(Form):
    name = StringField("name")
