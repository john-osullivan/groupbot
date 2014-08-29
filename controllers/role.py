__author__ = 'John'

from flask import Flask, request, session, g, redirect, url_for,\
     abort, render_template, flash, make_response
from flask.ext.sqlalchemy import SQLAlchemy,Pagination
from app import app
from models import db_session, User, Group, Member,Role

#----------------------------------------------------------------------------#
# Atomic Events for ROLES.
#----------------------------------------------------------------------------#
def create_role(group_id, request):
    '''
    INPUT
    Takes a Group_ID, optional Member_ID, and RoleForm -- which has the
    mandatory argument of a role name and an optional argument of role
    description.

    OUTPUT
    Creates a Role within the specified Group that has the specified description.
    If a Member_ID is supplied, that Member automatically becomes the first
    person to hold the Role.
    '''
    role_name = request.form['name']
    description = request.form['description'] if request.form['description'] else None
    member = int(request.form['member']) if request.form['member'] else None
    new_role = Role(group_id = group_id, name = role_name, \
                                description = description, member_id = member)
    db_session.add(new_role)
    db_session.commit()
    return new_role

def delete_role(role_id, request):
    '''
    INPUT
    Takes a Role_ID and a request holding a delete form.  If the form says perform the delete,
    it does it and returns True.  If it doesn't say do the delete, it returns False.

    OUTPUT
    Removes the Role's row from the database.  It is therefore no longer associated
    with any members.  If there are any Tasks only approved by that Role, then the
    approval responsibilities move to the people who were last holding said Role.
    '''
    role = Role.query.get(role_id)
    if request.form['delete']:
        db_session.delete(role)
        db_session.commit()
        return True
    else:
        return False

def edit_role(role_id, request):
    '''
    Takes a role and a request.  It updates the name and description of the Role based
    on the values in request.form, then it updates the set of Members who hold the role.
    :param role_id:
    :param request:
    :return:
    '''

    # First, grab our pretty little Role...
    this_role = Role.query.get(role_id)

    # Next, get all of its new values...
    new_name = request.form['name']
    new_description = request.form['description']
    new_members = [Member.query.get(member_id) for member_id in request.form['members']]

    # Then you actually modify the Role...
    this_role.name = new_name
    this_role.description = new_description
    this_role.members = new_members

    # Save your work, and then you're done!
    db_session.add(this_role)
    db_session.commit()
    return this_role