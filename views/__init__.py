__author__ = 'John'
import group, member, role, task, event, helper
from models import Task, Event
from flask.ext.login import current_user, login_user, logout_user

from flask import Flask, request, session, g, redirect, url_for,\
     abort, render_template, flash, make_response
from flask.ext.sqlalchemy import SQLAlchemy,Pagination
from app import app
from models import db_session, User, Bond, Group, Member, \
                                member_roles, Role, member_tasks, Task, \
                                Event, Infopage, Infoblock
from forms import *

__all__ = ['user', 'group', 'role', 'task', 'event', 'member']

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
    if form.validate_on_submit():
        user = User.query.filter_by(code_name=form.code_name).first()
        login_user(user)
        return redirect(url_for(group.group_list))
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
# Standard Infopage view functions
#---------------------------------------------#
###############################################
# def build_infonav(infopage):
#     '''
#     This function builds the object required to populate the nav on every page.
#     To do so, it goes up one level to the parent page and then gets all of the
#     children name and view functions going two levels down.  This means our
#     active page is open and all the others can also be opened without reloading.
#
#     :param infopage:
#     :return infonav:
#     '''
#     infonav = {}
#
#     # First, grab the info for the parent page
#     parent = infopage.parent
#     parent_name = parent.name
#     parent_endview = parent.end_view
#     infonav['parent'] = {'name':parent_name, 'end_view':parent_endview}
#
#     # Now the info for each of the current page's peers
#     infonav['pages'] = []
#     for page in parent.children:
#         page_listing = {}
#         page_listing['name'] = page.name
#         page_listing['end_view'] = page.end_view
#
#         # Make sure to go another layer deep if you need to.
#         if page.children != None:
#             page_listing['children'] = [{'name':child.name, 'end_view':child.end_view} for child in page.children]
#         infonav['pages'].append(page_listing)
#
#     return infonav
#
# def build_infopage(infopage):
#     '''
#     This function goes through the effort of building up the convoluted, general-ass
#     object that constitutes each and every one of our pages.  Specifically, it:
#     1) Grabs the info specific to the active page
#     2) Grabs the info for each infoblock using its content_func attribute
#
#     :param infopage:
#     :return:
#     '''
#     infonav = build_infonav(infopage)
#     info = {}
#     info['name'] = infopage.name
#     info['description'] = infopage.description
#     thing = class_table[]
#
#     return render_template('pages/infopage.html', infonav=infonav, infopage=info)



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

def build_infonav(level, current_group=None, member=None):
    '''
    This function produces the information required to construct the (now simplified) navbar.  The level
    parameter determines whether we should be passing in the list of groups (for the top-level dashboard view)
    or instead be passing in the information required to show one group (for the group detail view).

    :param level:
    :return infonav:
    '''

    # First, make our infonav object
    infonav = {}

    # If we're at the user level, we just need the sidebar to list each of the user's groups
    if level == 'user':
        infonav['parent'] = {'name': current_user.code_name,
                             'view': group.group_list}
        user_groups = helper.get_groups_from_user(current_user)
        infonav['pages'] = []
        for each_group in user_groups:
            infonav['pages'].append({
                'name':each_group.code_name,
                'view':group.group_detail
            })

    # At the group level, however, we want to list all the vital information from each group.
    # Namely, we need links to Tasks, Events, Roles, and Members.  Tasks and Events have the five
    # upcoming objects as children along with a link to the actual List page, Role and Member
    # have no children -- just a link to the list page.
    elif level == 'group':
        # First off, make sure the group is defined -- otherwise we're borked!
        if current_group == None:
            raise Exception("No Group supplied to create infonav!")
        else:
            # Assuming it's defined, get the parent listing set up
            infonav['parent'] = {'name': current_group.code_name,
                                 'view': group.group_detail,
                                 'args':{'group_id':current_group.group_id}}

            # Now the fun part.  First, add the links for Members and Roles
            infonav['pages'] = []
            infonav['pages'].append({
                'name':'Members',
                'view':member.member_list
            })
            infonav['pages'].append({
                'name':'Roles',
                'view':role.role_list
            })

            # Now, make the objects required to populate Tasks and its children
            task_view = {'name':'Tasks',
                         'view':task.task_list}
            upcoming_tasks = Task.query.filter_by(group_id = current_group.id).order_by(Task.deadline).limit(5)
            task_view['children'] = []
            for each_task in upcoming_tasks:
                task_view['children'].append({'name':each_task.name,
                                              'view':task.task_detail,
                                              'args':{'task_id':each_task.task_id}})
            infonav['pages'].append(task_view)

            # Same story, but now with the Group's Events
            event_view = {'name':'Events',
                          'view':event.event_list}
            upcoming_events = Event.query.filter_by(group_id = current_group.id).order_by(Event.start_time).limit(5)
            for each_event in upcoming_events:
                event_view['children'].append({'name':each_event.name,
                                               'view':event.event_detail,
                                               'args':{'event_id':each_event.event_id}})
            infonav['pages'].append(event_view)


    return infonav