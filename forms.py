from flask_wtf import Form
from wtforms import TextField, DateField, IntegerField, \
        SelectField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Length

# Set your classes here.

class RegisterForm(Form):
    username = TextField('Username', validators=[Length(min=6, max=30), DataRequired()])
    password    = PasswordField('Password', validators = [DataRequired(), Length(min=6, max=40)])
    confirm     = PasswordField('Repeat Password', [DataRequired(), EqualTo('password', message='Passwords must match')])
    name        = TextField('Real/Display Name', validators = [Length(min=6, max=40)])
    email       = TextField('Email', validators = [DataRequired(), Length(min=6, max=40)])
    phone = FormField(TelephoneForm)
    bio = TextField('Bio', validators = [Length(min=1, max=160)])
  
class PasswordChangeForm(Form):
    old_password = Password('Old Password', validators = [Length(min=6, max=40)])
    password = Password('New Password', validators = [Length(min=6, max=40)])
    confirm =   Password('Confirm NewPassword', validators = [Length(min=6, max=40)])

class UserInfoChangeForm(Form):
    name        = TextField('Real/Display Name', validators = [Length(min=6, max=40)])
    phone = FormField(TelephoneForm)
    bio = TextField('Bio', validators = [Length(min=1, max=160)])

class EmailChangeForm(Form):
    email       = TextField('New Email', validators = [DataRequired(), Length(min=6, max=40)])

class TelephoneForm(Form):
    country_code = IntegerField('Country Code', [validators.required()])
    area_code    = IntegerField('Area Code/Exchange', [validators.required()])
    number       = TextField('Number')

class LoginForm(Form):
    name        = TextField('Username', [DataRequired()])
    password    = PasswordField('Password', [DataRequired()])

class ForgotForm(Form):
    email       = TextField('Email', validators = [DataRequired(), Length(min=6, max=40)])

class GroupForm(Form):
    human_name = TextField('Group "Human Name"', validators=[DataRequired(), Length(min=6, max=80)])
    code_name = TextField('Group "Code Name"', validators=[DataRequired(), Length(min=6, max=80)])
    byline = TextField('Group By-Line', validators=[Length(min=6, max=160)])
    description = TextField('Group Description', validators=[Length(min=40, max=2048)])

class MemberForm(Form):
    preferred_name = TextField('Preferred Name', validators=[Length(min=6, max=80)])

class RoleForm(Form):
    name = TextField('Title', validators=[DataRequired(), Length(min=6, max=80)])
    description = TextField('Description', validators=[Length(min=40, max=2048)])

class TaskForm(Form):
    name = TextField('Task Title', validators=[DataRequired(), Length(min=6, max=80)])
    description = TextField('Task Description', validators=[Length(min=6, max=512)])
    assignee = FormField(MemberForm)
    deadline = DateField('Deadline')
    points = IntegerField('Point Value')
    comments = TextField('Comments', validators=[Length(min=6, max=256)])