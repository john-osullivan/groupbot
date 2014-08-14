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


@app.route('/group/<group_code_name>/tasks')
def task_list(group_code_name, task_id):
    '''
    '''
    return render_template('templates/pages/tasks/list')

@app.route('/group/<group_code_name>/tasks/<task_id>')
def task_detail(group_code_name, task_id):
    '''
    A complete view of all information relevant to a task, aka the detail view.
    This would include giving, do-er, deliverable, deadline, description, approval
    status.
    '''
    return render_template('templates/pages/tasks/detail')

@app.route('/group/<group_code_name>/tasks/<task_id>/edit')
def task_edit(group_code_name, task_id):
    '''
    '''
    return render_template('templates/pages/tasks/edit')

@app.route('/group/<group_code_name>/tasks/<task_id>/delete')
def task_edit(group_code_name, task_id):
    '''
    '''
    return render_template('templates/pages/tasks/delete')