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

@app.route('/group/<group_code_name>/roles/<role_id>/list')
def role_list(group_code_name, role_id):
    '''

    '''
    return render_template('templates/pages/roles/list')

@app.route('/group/<group_code_name>/roles/<role_id>')
def role_detail(group_code_name, role_id):
    '''
    A complete view of all the information relevant to a role.  This would include
    all Tasks given to or from the Role, all Events hosted with its permission,
    a link to its Info, and a list of all Members who are performing it.  Additionally
    it would have links
    '''
    return render_template('templates/pages/roles/detail')

@app.route('/group/<group_code_name>/roles/<role_id>/edit')
def role_edit(group_code_name, role_id):
    '''

    '''
    return render_template('templates/pages/roles/edit')

@app.route('/group/<group_code_name>/roles/<role_id>/delete')
def role_delete(group_code_name, role_id):
    '''
    '''
    return render_template('templates/pages/roles/delete')