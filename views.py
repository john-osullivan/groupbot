from flask import Flask, request, session, g, redirect, url_for,\
     abort, render_template, flash, make_response
from flask.ext.sqlalchemy import SQLAlchemy,Pagination
from app import app
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





###############################################
#---------------------------------------------#
# Controllers.
#---------------------------------------------#
###############################################

@app.route('/')
def home():
    return render_template('pages/home.html')

@app.route('/about')
def about():
    return render_template('pages/about.html')

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

###############################################
#---------------------------------------------#
# View Pages
#---------------------------------------------#
###############################################
@app.route('/dashboard')
def dashboard():
    '''
    View which combines a list of quick summaries concerning the goings-on
    for each of your groups.
    '''

@app.route('/group/<group_code_name>')
def view_group(group_code_name):
    '''
    In-depth view of the recent activity of the group, including everything
    pertaining to the specific member viewing it.  The group can mark
    specific content as public and viewable by anonymous members if it so
    chooses (think of it like combining your management and your publicity
    into the same activity).
    '''

@app.route('/group/<group_code_name>/task/<task_id>')
def view_task(group_code_name, task_id):
    '''
    A complete view of all information relevant to a task, aka the detail view.
    This would include giving, do-er, deliverable, deadline, description, approval
    status.
    '''

@app.route('/group/<group_code_name>/event/<event_id>')
def view_event(group_code_name, event_id):
    '''
    A complete view of all information relevant to an event, aka the detail view.
    This would include the host, start time, end time, 
    '''

@app.route('/group/<group_code_name>/role/<role_id>')
def view_role(group_code_name, role_id):
    '''
    A complete view of all the information relevant to a role.  This would include
    all Tasks given to or from the Role, all Events hosted with its permission,
    a link to its Info, and a list of all Members who are performing it.  Additionally
    it would have links 
    '''

@app.route('/group/<group_code_name>/info/<info_id>')
def view_info(group_code_name, info_id):
    '''
    This displays the info page.  It should essentially boil down to rendering the
    HTML string within the structure of the page we define. 
    '''

###############################################
#---------------------------------------------#
# Edit Pages
#---------------------------------------------#
###############################################
@app.route('/group/<group_code_name>/edit')
def edit_group_view(group_code_name):
    '''
    '''

@app.route('/group/<group_code_name>/event/<event_id>/edit')
def edit_event_view(group_code_name, event_id):
    '''
    '''

@app.route('/group/<group_code_name>/task/<task_id>/edit')
def edit_task_view(group_code_name, task_id):
    '''
    '''

@app.route('/group/<group_code_name>/info/<info_id>/edit')
def edit_info_view(group_code_name, info_id):
    '''
    '''

@app.route('/group/<group_code_name>/role/<role_id>/edit')
def edit_role_view(group_code_name, role_id):
    '''
    '''

@app.route('/group/<group_code_name>/member/<member_id>/edit')
def edit_member_view(group_code_name, member_id):
    '''
    '''

###############################################
#---------------------------------------------#
# Error Handlers
#---------------------------------------------#
###############################################

@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500

@app.errorhandler(404)
def internal_error(error):
    return render_template('errors/404.html'), 404