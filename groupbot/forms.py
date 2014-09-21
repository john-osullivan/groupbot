from wtforms import Form, StringField, DateField, IntegerField, \
        SelectField, PasswordField, FormField, RadioField, SelectMultipleField,\
        DateTimeField, TextAreaField, FileField, FieldList
from wtforms.validators import DataRequired, EqualTo, Length

# Set your classes here.

class TelephoneForm(Form):
    country_code = IntegerField('Country Code', validators = [DataRequired()])
    area_code = IntegerField('Area Code/Exchange', validators = [DataRequired()])
    number = StringField('Number', validators = [DataRequired()])

class RealNameForm(Form):
    first_name = StringField('First Name', validators = [Length(min=2, max=32)])
    last_name = StringField('Last Name', validators = [Length(min=2, max=32)])

class UserCreateForm(Form):
    name = FormField(RealNameForm)
    codename = StringField('Codename', validators=[Length(min=6, max=30), DataRequired()])
    password = PasswordField('Password', validators = [DataRequired(), Length(min=6, max=40)])
    confirm = PasswordField('Repeat Password', [DataRequired(), EqualTo('password', message='Passwords must match')])
    email  = StringField('Email', validators = [DataRequired(), Length(min=6, max=40)])
    phone = FormField(TelephoneForm)
    photo = FileField('Photo URL')
    bio = StringField('Bio', validators = [Length(min=1, max=160)])
  
class PasswordChangeForm(Form):
    old_password = PasswordField('Old Password', validators = [Length(min=6, max=40)])
    password = PasswordField('New Password', validators = [Length(min=6, max=40)])
    confirm =   PasswordField('Confirm NewPassword', validators = [Length(min=6, max=40)])

class UserEditForm(Form):
    code_name = StringField('Codename', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    name = FormField(RealNameForm)
    phone = FormField(TelephoneForm)
    bio = TextAreaField('Bio', validators = [Length(min=1, max=160)])
    photo = StringField('Photo URL')

class EmailChangeForm(Form):
    email       = StringField('New Email', validators = [DataRequired(), Length(min=6, max=40)])

class LoginForm(Form):
    codename        = StringField('Username (aka codename)', [DataRequired()])
    password    = PasswordField('Password', [DataRequired()])

class ForgotForm(Form):
    email       = StringField('Email', validators = [DataRequired(), Length(min=6, max=40)])

class GroupForm(Form):
    human_name = StringField('Group Display Name', validators=[DataRequired(), Length(min=6, max=80)])
    code_name = StringField('Group "Code Name"', validators=[DataRequired(), Length(min=6, max=80)])
    byline = StringField('Group By-Line', validators=[Length(min=6, max=160)])
    description = TextAreaField('Group Description', validators=[Length(min=40, max=2048)])

class SignatureForm(Form):
    signature = StringField('User Codename', validators=[DataRequired()])

class DeleteForm(Form):
    delete = RadioField("Delete?", choices=[(True, "Yup, do it."), (False, "No, I didn't mean it!")])

class SignedDeleteForm(Form):
    signature_field = FormField(SignatureForm)
    delete = FormField(DeleteForm)

class MemberEditForm(Form):
    codename = StringField('Member Codename', validators=[Length(min=6, max=80)])
    bio = TextAreaField('Bio', validators=[Length(min=6, max=256)])
    photo = StringField('Photo URL')

class SingleMemberForm(Form):
    member = SelectField('Member', coerce=int, validators=[DataRequired()])

class MultipleMemberForm(Form):
    members = SelectMultipleField('Member(s)', coerce=int, validators=[DataRequired()])

class MemberInviteForm(Form):
    user_codename = StringField('User Codename')
    user_email = FieldList('User (or New User!) Email Address')

class MultipleRoleForm(Form):
    roles = SelectMultipleField('Role', coerce=int, validators=[DataRequired()])

class RoleForm(Form):
    name = StringField('Title', validators=[DataRequired(), Length(min=6, max=80)])
    description = TextAreaField('Description', validators=[Length(min=40, max=2048)])
    members = FormField(MultipleMemberForm)

class SingleRoleForm(Form):
    role = SelectField('Role', coerce=int, validators=[DataRequired()])

class RoleAssignForm(Form):
    role = FormField(SingleRoleForm)
    member = FormField(MultipleMemberForm)

class TaskForm(Form):
    name = StringField('Task Title', validators=[DataRequired(), Length(min=6, max=80)])
    description = StringField('Task Description', validators=[Length(min=6, max=512)])
    approving_members = FormField(MultipleMemberForm)
    approving_roles = FormField(MultipleRoleForm)
    delivering_members = FormField(MultipleMemberForm)
    delivering_roles = FormField(MultipleRoleForm)
    deliverable = StringField('Deliverable', validators=[Length(min=6, max=256)])
    deadline = DateField('Deadline')
    comments = StringField('Comments', validators=[Length(min=6, max=256)])

class TaskDeliverForm(Form):
    signature = StringField('Signature', validators=[DataRequired()])

class TaskApproveForm(Form):
    signature = StringField('Signature', validators=[DataRequired()])

class EventForm(Form):
    name = StringField('Event Name', validators=[DataRequired(), Length(min=6, max=80)])
    start_time = DateTimeField('Starting Time', validators=[DataRequired()])
    end_time = DateTimeField('Ending Time')
    location = StringField('Event Location', validators=[DataRequired(), Length(min=6, max=80)])
    description = TextAreaField('Event Description', validators=[Length(min=6, max=1024)])
    host_members = FormField(MultipleMemberForm, validators=[DataRequired()])
    host_roles = FormField(MultipleRoleForm)
    visible_to_uninvited = RadioField("Is this Event visible to Members who aren't invited?",
                                      choices=[(True, "Yup, anyone can see it!"), (False, "No, it's secret.")],
                                      default=True,
                                      validators=[DataRequired()])
    invited_can_invite = RadioField("Can invited Members invite more Members?",
                                    choices=[(True, "Sure, invited everyone!"), (False, "No, only the hosts.")],
                                    default=False,
                                    validators=[DataRequired()])

class EventChoiceForm(Form):
    event = SelectField('Event Name',coerce=int)

class EventInviteForm(Form):
    invited_roles = FormField(MultipleRoleForm)
    invited_members = FormField(MultipleMemberForm)

class EventRSVPForm(Form):
    attending = RadioField("Attending?", choices=[(True, "Yup, I'll be there!"), (False, "Nope, can't make it.")],
                           validators=[DataRequired()])

class EventAttendanceForm(Form):
    attended = FormField(MultipleMemberForm)
