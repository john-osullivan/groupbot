from flask_wtf import Form
from wtforms import TextField, DateField, IntegerField, \
        SelectField, PasswordField, FormField, RadioField, SelectMultipleField,\
        DateTimeField, TextAreaField, FileField, FieldList
from wtforms.validators import DataRequired, EqualTo, Length

# Set your classes here.

class TelephoneForm(Form):
    country_code = IntegerField('Country Code', validators = [DataRequired()])
    area_code    = IntegerField('Area Code/Exchange', validators = [DataRequired()])
    number       = TextField('Number', validators = [DataRequired()])

class RealNameForm(Form):
    first_name = TextField('First Name', validators = [Length(min=2, max=32)])
    last_name = TextField('Last Name', validators = [Length(min=2, max=32)])

class RegisterForm(Form):
    username = TextField('Username', validators=[Length(min=6, max=30), DataRequired()])
    password = PasswordField('Password', validators = [DataRequired(), Length(min=6, max=40)])
    confirm = PasswordField('Repeat Password', [DataRequired(), EqualTo('password', message='Passwords must match')])
    name = FormField(RealNameForm)
    email  = TextField('Email', validators = [DataRequired(), Length(min=6, max=40)])
    phone = FormField(TelephoneForm)
    bio = TextField('Bio', validators = [Length(min=1, max=160)])
  
class PasswordChangeForm(Form):
    old_password = PasswordField('Old Password', validators = [Length(min=6, max=40)])
    password = PasswordField('New Password', validators = [Length(min=6, max=40)])
    confirm =   PasswordField('Confirm NewPassword', validators = [Length(min=6, max=40)])

class UserEditForm(Form):
    code_name = TextField('Codename', validators=[DataRequired()])
    email = TextField('Email', validators=[DataRequired()])
    name = FormField(RealNameForm)
    phone = FormField(TelephoneForm)
    bio = TextAreaField('Bio', validators = [Length(min=1, max=160)])
    photo = TextField('Photo URL')

class EmailChangeForm(Form):
    email       = TextField('New Email', validators = [DataRequired(), Length(min=6, max=40)])

class LoginForm(Form):
    code_name        = TextField('Username (aka codename)', [DataRequired()])
    password    = PasswordField('Password', [DataRequired()])

class ForgotForm(Form):
    email       = TextField('Email', validators = [DataRequired(), Length(min=6, max=40)])

class GroupForm(Form):
    human_name = TextField('Group Display Name', validators=[DataRequired(), Length(min=6, max=80)])
    code_name = TextField('Group "Code Name"', validators=[DataRequired(), Length(min=6, max=80)])
    byline = TextField('Group By-Line', validators=[Length(min=6, max=160)])
    description = TextAreaField('Group Description', validators=[Length(min=40, max=2048)])

class DeleteForm(Form):
    delete = RadioField("Delete?", choices=[(True, "Yup, do it."), (False, "No, I didn't mean it!")])

class MemberEditForm(Form):
    preferred_name = TextField('Preferred Name', validators=[Length(min=6, max=80)])
    bio = TextAreaField('Bio', validators=[Length(min=6, max=256)])
    photo = TextField('Photo URL')

class SingleMemberForm(Form):
    member = SelectField('Member', coerce=int, validators=[DataRequired()])

class MultipleMemberForm(Form):
    members = SelectMultipleField('Member(s)', coerce=int, validators=[DataRequired()])

class MemberInviteForm(Form):
    code_names = TextField('User Codename')
    email_addresses = FieldList('User (or New User!) Email Address')

class MultipleRoleForm(Form):
    role = SelectMultipleField('Role', coerce=int, validators=[DataRequired()])

class RoleForm(Form):
    name = TextField('Title', validators=[DataRequired(), Length(min=6, max=80)])
    description = TextField('Description', validators=[Length(min=40, max=2048)])
    member = FormField(MultipleMemberForm)

class SingleRoleForm(Form):
    role = SelectField('Role', coerce=int, validators=[DataRequired()])

class RoleAssignForm(Form):
    role = FormField(SingleRoleForm)
    member = FormField(MultipleMemberForm)

class TaskForm(Form):
    name = TextField('Task Title', validators=[DataRequired(), Length(min=6, max=80)])
    description = TextField('Task Description', validators=[Length(min=6, max=512)])
    doing_member = FormField(MultipleMemberForm)
    deadline = DateField('Deadline')
    comments = TextField('Comments', validators=[Length(min=6, max=256)])

class TaskDeliverForm(Form):
    task = SelectField('Task', validators=[DataRequired()])
    signature = TextField('Signature', validators=[DataRequired()])
    report = TextField('Message', validators=[Length(min=6, max=2048)])
    deliverable = FileField('Deliverable')

class EventForm(Form):
    name = TextField('Event Name', validators=[DataRequired(), Length(min=6, max=80)])
    hosts = FormField(MultipleMemberForm, validators=[DataRequired()])
    start_time = DateTimeField('Starting Time', validators=[DataRequired()])
    end_time = DateTimeField('Ending Time')
    location = TextField('Event Location', validators=[DataRequired(), Length(min=6, max=80)])
    description = TextAreaField('Event Description', validators=[Length(min=6, max=1024)])

class EventChoiceForm(Form):
    event = SelectField('Event Name',coerce=int)

class EventInviteForm(Form):
    event = FormField(EventChoiceForm)
    members = FormField(MultipleMemberForm)

class EventRSVPForm(Form):
    event = FormField(EventChoiceForm)
    attending = RadioField("Attending?", choices=[(True, 'Yes'), (False, 'No')])

class EventAttendanceForm(Form):
    event = FormField(EventChoiceForm)
    attended = FormField(MultipleMemberForm)
    absent = FormField(MultipleMemberForm)
