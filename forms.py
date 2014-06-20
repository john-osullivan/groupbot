from flask_wtf import Form
from wtforms import TextField, DateField, IntegerField, \
        SelectField, PasswordField, FormField
from wtforms.validators import DataRequired, EqualTo, Length

# Set your classes here.

class TelephoneForm(Form):
    country_code = IntegerField('Country Code', validators = [DataRequired()])
    area_code    = IntegerField('Area Code/Exchange', validators = [DataRequired()])
    number       = TextField('Number', validators = [DataRequired()])

class RegisterForm(Form):
    username = TextField('Username', validators=[Length(min=6, max=30), DataRequired()])
    password    = PasswordField('Password', validators = [DataRequired(), Length(min=6, max=40)])
    confirm     = PasswordField('Repeat Password', [DataRequired(), EqualTo('password', message='Passwords must match')])
    name        = TextField('Real/Display Name', validators = [Length(min=6, max=40)])
    email       = TextField('Email', validators = [DataRequired(), Length(min=6, max=40)])
    phone = FormField(TelephoneForm)
    bio = TextField('Bio', validators = [Length(min=1, max=160)])
  
class PasswordChangeForm(Form):
    old_password = PasswordField('Old Password', validators = [Length(min=6, max=40)])
    password = PasswordField('New Password', validators = [Length(min=6, max=40)])
    confirm =   PasswordField('Confirm NewPassword', validators = [Length(min=6, max=40)])

class UserEditForm(Form):
    name        = TextField('Real/Display Name', validators = [Length(min=6, max=40)])
    phone = FormField(TelephoneForm)
    bio = TextField('Bio', validators = [Length(min=1, max=160)])

class EmailChangeForm(Form):
    email       = TextField('New Email', validators = [DataRequired(), Length(min=6, max=40)])

class LoginForm(Form):
    name        = TextField('Username', [DataRequired()])
    password    = PasswordField('Password', [DataRequired()])

class ForgotForm(Form):
    email       = TextField('Email', validators = [DataRequired(), Length(min=6, max=40)])

class GroupForm(Form):
    human_name = TextField('Group Display Name', validators=[DataRequired(), Length(min=6, max=80)])
    code_name = TextField('Group "Code Name"', validators=[DataRequired(), Length(min=6, max=80)])
    byline = TextField('Group By-Line', validators=[Length(min=6, max=160)])
    description = TextField('Group Description', validators=[Length(min=40, max=2048)])

class MemberEditForm(Form):
    preferred_name = TextField('Preferred Name', validators=[Length(min=6, max=80)])

class MemberChoiceForm(Form):
    member = SelectField('Member', coerce=int, validators=[DataRequired()])

class RoleChoiceForm(Form):
    role = SelectField('Role', coerce=int, validators=[DataRequired()])

class RoleForm(Form):
    name = TextField('Title', validators=[DataRequired(), Length(min=6, max=80)])
    description = TextField('Description', validators=[Length(min=40, max=2048)])

class RoleAssignForm(Form):
    role = FormField(RoleChoiceForm)
    member = FormField(MemberChoiceForm)
 
class TaskForm(Form):
    name = TextField('Task Title', validators=[DataRequired(), Length(min=6, max=80)])
    description = TextField('Task Description', validators=[Length(min=6, max=512)])
    doing_member = FormField(MemberForm)
    deadline = DateField('Deadline')
    points = IntegerField('Point Value')
    comments = TextField('Comments', validators=[Length(min=6, max=256)])

class TaskDeliverForm(Form):
    # This one is an interesting question.  What delivery methods do we want to support
    # up front? -JJO

class EventForm(Form):
    name = TextField('Event Name', validators=[DataRequired(), Length(min=6, max=80)])
    host_id = FormField(MemberChoiceForm, validators=[DataRequired()])
    start_time = DateField('Starting Time', validators=[DateRequired()])
    end_time = DateField('Ending Time')
    location = TextField('Event Location', validators=[DataRequired(), Length(min=6, max=80)])
    description = TextField('Event Description', validators=[Length(min=6, max=1024)])

class EventChoiceForm(Form):
    event = SelectField('Event Name',coerce=int)

class EventInviteForm(Form):
    event = FormField(EventChoiceForm)
    member = FormField(MemberChoiceForm)

class EventRSVPForm(Form):
    event = FormField(EventChoiceForm)
    attending = RadioField("Attending?", choices=[(True, 'Yes'), (False, 'No')])

class EventAttendanceForm(Form):
    event = FormField(EventChoiceForm)
    member = FormField(MemberChoiceForm)
    attended = RadioField("Attended?", choices=[(True, 'Yes'), (False, 'No')])

class InfoPageForm(Form):
