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

@app.route('/group/<group_code_name>/members')
def member_list(group_code_name, member_code_name):
    '''
    This thing gives you a view of all the Members in the Group

    :param group_code_name:
    :param member_code_name:
    :return:
    '''
    return render_template('templates/pages/members/list')

@app.route('/group/<group_code_name>/members/<member_code_name>')
def member_detail(group_code_name, member_code_name):
    '''

    :param group_code_name:
    :param member_code_name:
    :return:
    '''
    return render_template('templates/pages/members/detail')

@app.route('/group/<group_code_name>/members/<member_code_name>/edit')
def member_edit(group_code_name, member_code_name):
    return render_template('templates/pages/members/edit')

@app.route('/group/<group_code_name>/members/<member_code_name>/delete')
def member_delete(group_code_name, member_code_name):
    return render_template('templates/pages/members/delete')