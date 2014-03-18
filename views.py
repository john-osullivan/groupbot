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
    return None

@app.route('/deleteUser')
def delete_user():
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

# Gives or removes a Role from a specific Member
@app.route('/assignRole')
def assign_role():
    return None

#----------------------------------------------------------------------------#
# Tasks.
#----------------------------------------------------------------------------#

@app.route('/createTask')
def create_task():
    return None

@app.route('/deleteTask')
def delete_task():
    return None

# Used to deliver & approve tasks.
@app.route('/returnTask')
def return_task():
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