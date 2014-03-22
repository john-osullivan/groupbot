from flask import Flask, request, session, g, redirect, url_for,\
     abort, render_template, flash, make_response
from flask.ext.sqlalchemy import SQLAlchemy,Pagination
from models import db_session, User, GroupPartnership, Group, Member, \
                                member_roles, Role, member_tasks, Task


# Login required decorator.
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

##############################################
#----------------------------------------------------------------------------#
# Data Manipulators.
#----------------------------------------------------------------------------#
##############################################

#----------------------------------------------------------------------------#
# Users.
#----------------------------------------------------------------------------#
@app.route('/createUser')
def create_user():
    '''
    INPUT
    User Form with the mandatory arguments username, password, and email.
    Optional arguments real/display name, phone number, and 160 character
    bio.

    REQUIREMENT
    Username and email must be unique.

    OUTPUT
    Creates a User row in the database with all of the provided information
    associated with it.
    '''
    return None

@app.route('/deleteUser')
def delete_user():
    '''
    INPUT
    User_ID of the account to be deleted.

    OUTPUT
    Removes the user's row from the database, purging all of their memberships.
    '''
    return None

@app.route('/editUser')
def edit_user():
    '''
    INPUT
    A PasswordChangeForm, EmailChangeForm, or UserInfoChangeForm,
    along with the user's ID from the request.

    OUTPUT
    Modifies the user's row in the database as specified by whichever form
    was submitted
    '''
    return None

#----------------------------------------------------------------------------#
# Groups.
#----------------------------------------------------------------------------#

@app.route('/createGroup')
def create_group():
    '''
    INPUT
    Takes a GroupForm with the mandatory arguments of DIsplay Name
    and Code Name, optional argumets of By-Line and Description.

    OUTPUT
    Creates a new Group with the specified information.  The User who
    created the Group is both its first Member and the administrator (which
    is the default first role in every group).
    '''
    return None

@app.route('/deleteGroup')
def delete_group():
    '''
    INPUT
    Takes the ID of the group and the User_ID of the person who submitted
    the request for deletion.

    OUTPUT
    Deletes the Group from the database, including all of its Members, Roles,
    and Tasks.  If the User_ID does not match up with that of
    the administrator, the request does not succeed.
    '''
    return None

@app.route('/createPartnership')
def create_partnership():
    '''
    INPUT
    Takes the IDs of the partnership and the new partner.

    OUTPUT
    Add the partner to the Partnership Group's Partners relation.  Conversely, 
    it also adds    the partnership to the partner's Partnerships relation.  If the
    groups are already partnered, nothing happens.  If the groups are already
    part of a parent or child relationship with each other, nothing happens.
    '''
    return None

@app.route('/createSubgrouping')
def create_subgrouping():
    '''
    INPUT
    Takes the IDs of the parent and child groups.

    OUTPUT
    Sets the child's parent_id attribute to the ID of the parent group.  Adds the
    child's ID to the parent's children ForeignKey relation.
    '''
    return None

#----------------------------------------------------------------------------#
# Members.
#----------------------------------------------------------------------------#

@app.route('/addMember')
def add_member():
    '''
    INPUT
    A group ID, a user ID, and a Member Form which only has one (optional)
    argument of a Preferred Name.  Letting people decide who they are based
    on where they are is generally a nice thing.

    OUTPUT
    Create a new Member row associated with the User and Group, possibly
    holding a value for Preferred Name.  The Role and Task relations are 
    empty by default. 
    '''
    return None

@app.route('/removeMember')
def remove_member():
    '''
    INPUT
    A group ID and Member ID for the member to be removed.

    OUTPUT
    Removes the specified Member's row from the database, removing them 
    from all Roles they were assigned to.  If a Task was only assigned to them,
    it is removed as well.
    '''
    return None

#----------------------------------------------------------------------------#
# Roles.
#----------------------------------------------------------------------------#

@app.route('/createRole')
def create_role():
    '''
    INPUT
    Takes a Group_ID, optional Member_ID, and RoleForm -- which has the 
    mandatory argument of a role name and an optional argument of role
    description.

    OUTPUT
    Creates a Role within the specified Group that has the specified descrption.
    If a Member_ID is supplied, that Member automatically becomes the first 
    person to hold the Role.
    '''
    return None

@app.route('/deleteRole')
def delete_role():
    '''
    INPUT
    Takes a Group_ID and Role_ID to be deleted.

    OUTPUT
    Removes the Role's row from the database.  It is therefore no longer associated
    with any members.  If there are any Tasks only approved by that Role, then the
    approval responsibilities move to the people who were last holding said Role.
    '''
    return None

# Gives a Role to a specific Member
@app.route('/assignRole')
def assign_role():
    '''
    INPUT
    Takes a Group_ID, Role_ID, and Member_ID.

    OUTPUT
    Adds the Member to the Member_ID propety of the specified Role in the
    specified Group.  If the Member is already assigned to the Role, throws an
    Exception saying that Role was already assigned to that Member.
    '''
    return None

@app.route('/removeRole')
def remove_role():
    '''
    INPUT
    Takes a Group_ID, Role_ID, and Member_ID.

    OUTPUT
    Removes the specified Member from the specified Role's Member_ID
    relation.  If the Member was not actually in that relation, throws an 
    Exception saying the specified Member did not have that Role.
    '''
    return None

#----------------------------------------------------------------------------#
# Tasks.
#----------------------------------------------------------------------------#

@app.route('/createTask')
def create_task():
    '''
    INPUT
    Takes in a submission of the create task form, gathering the Title, 
    Description, Deadline, Assignee, and optional Points arguments.  Also takes
    the Group ID and Assigner ID implicitly from the page request.

    OUTPUT
    Creates a new Task entry in the database associated with all relevant
    parties, adding it to the Tasks for each Member assigned.
    '''
    return None

@app.route('/deleteTask')
def delete_task():
    '''
    INPUT
    Triggered via a close button element, handed the task_id implicitly from the
    page request.

    REQUIREMENT
    Can only be used before a task has been delivered.

    OUTPUT
    Removes a Task entry from the database, erasing it from the Tasks of each
    Member.
    '''
    return None

# Used to deliver tasks.
@app.route('/deliverTask')
def deliver_task():
    '''
    INPUT
    Triggered via a delivery mechanism.  Only requires the task_id and a reference
    to the deliverable which completed it.  If an already delivered task is delivered
    again, the new deliverable overwrites the old one.

    OUTPUT
    Changes the delivered Boolean of the specified Task to True.
    '''
    return None

@app.route('/approveTask')
def approve_task():
    '''
    INPUT
    Requires the task_id and the ID of the request submitter.  Checks to make 
    sure the person approving the task is one of the people who assigned it.

    OUTPUT
    Changes the approved boolean of the task to True.  If Points are enabled,
    the points are then awarded to the doer of the task.
    '''
    return None



###############################################
#-----------------------------------------------------------------------------#
# Controllers.
#-----------------------------------------------------------------------------#
###############################################

@app.route('/')
def home():
    return render_template('pages/placeholder.home.html')

@app.route('/about')
def about():
    return render_template('pages/placeholder.about.html')

@app.route('/login')
def login():
    form = LoginForm(request.form)
    return render_template('forms/login.html', form = form)

@app.route('/register')
def register():
    form = RegisterForm(request.form)
    return render_template('forms/register.html', form = form)

@app.route('/forgot')
def forgot():
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form = form)

# Error handlers.

@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500

@app.errorhandler(404)
def internal_error(error):
    return render_template('errors/404.html'), 404