__author__ = 'John'

from flask import Flask, request, session, g, redirect, url_for,\
     abort, render_template, flash, make_response
from flask.ext.sqlalchemy import SQLAlchemy,Pagination
from app import app
from views import login_required
from models import db_session, User, Bond, Group, Member, \
                                member_roles, Role, member_tasks, Task, \
                                Event, Infopage, Infoblock
from forms import *

@app.route('/group/<group_code_name>/events')
def event_list(group_code_name, event_id):
    '''
    A complete view of all information relevant to an event, aka the detail view.
    This would include the host, start time, end time,
    '''
    return render_template('templates/pages/events/list')

@app.route('/group/<group_code_name>/events/<event_id>')
def event_detail(group_code_name, event_id):
    '''
    A complete view of all information relevant to an event, aka the detail view.
    This would include the host, start time, end time,
    '''
    return render_template('templates/pages/events/detail')

@app.route('/group/<group_code_name>/events/<event_id>/edit')
def event_edit(group_code_name, event_id):
    '''
    '''
    return render_template('templates/pages/events/edit')

@app.route('/group/<group_code_name>/events/<event_id>/delete')
def event_delete(group_code_name, event_id):
    '''
    '''
    return render_template('templates/pages/events/delete')