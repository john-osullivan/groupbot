from flask_wtf import Form
from wtforms import TextField, DateField, IntegerField, \
        SelectField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Length

# Set your classes here.

class RegisterForm(Form):
    name        = TextField('Username', validators = [DataRequired(), Length(min=6, max=25)])
    email       = TextField('Email', validators = [DataRequired(), Length(min=6, max=40)])
    password    = PasswordField('Password', validators = [DataRequired(), Length(min=6, max=40)])
    phone = FormField(TelephoneForm)
    bio = TextField('Bio', validators = [Length(min=1, max=160)])
    confirm     = PasswordField('Repeat Password', [DataRequired(), EqualTo('password', message='Passwords must match')])

class TelephoneForm(Form):
    country_code = IntegerField('Country Code', [validators.required()])
    area_code    = IntegerField('Area Code/Exchange', [validators.required()])
    number       = TextField('Number')

class LoginForm(Form):
    name        = TextField('Username', [DataRequired()])
    password    = PasswordField('Password', [DataRequired()])

class ForgotForm(Form):
    email       = TextField('Email', validators = [DataRequired(), Length(min=6, max=40)])
