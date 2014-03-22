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
    return None

@app.route('/deleteGroup')
def delete_group():
    return None

@app.route('/addPartner')
def add_subgroup():
    return None

@app.route('/joinPartnership')
def join_partnership():
    return None

@app.route('/joinParentGroup')
def join_parent_group():
    return None

@app.route('/addChildGroup')
def add_child_group():
    return None

#----------------------------------------------------------------------------#
# Members.
#----------------------------------------------------------------------------#

@app.route('/addMember')
def add_member():
    return None

@app.route('/removeMember')
def remove_member():
    return None

#----------------------------------------------------------------------------#
# Roles.
#----------------------------------------------------------------------------#

@app.route('/createRole')
def create_role():
    return None

@app.route('/deleteRole')
def delete_role():
    return None

# Gives a Role to a specific Member
@app.route('/assignRole')
def assign_role():
    return None

@app.route('/removeRole')
def remove_role():
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

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

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