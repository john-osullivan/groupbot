__author__ = 'John'

from flask import Flask, request, session, g, redirect, url_for,\
     abort, render_template, flash, make_response
from flask.ext.sqlalchemy import SQLAlchemy,Pagination
from app import app
from models import db_session, Group

#----------------------------------------------------------------------------#
# Atomic Events for GROUPS.
#----------------------------------------------------------------------------#
def create_group(request):
    '''
    INPUT
    Takes a GroupForm with the mandatory arguments of DIsplay Name
    and Code Name, optional argumets of By-Line and Description.

    OUTPUT
    Creates a new Group with the specified information.  The User who
    created the Group is both its first Member and the administrator (which
    is the default first role in every group).
    '''
    byline = request.form['byline'] if request.form['byline'] else None
    description = request.form['description'] if request.form['description'] else None
    new_group = Group(human_name = request.form['display_name'], \
                                    code_name = request.form['code_name'], \
                                    byline = byline, description = description)
    db_session.add(new_group)
    db_session.commit()
    return True

def delete_group(group_code_name):
    '''
    INPUT
    Takes the ID of the group and the User_ID of the person who submitted
    the request for deletion.

    OUTPUT
    Deletes the Group from the database, including all of its Members, Roles,
    and Tasks.  If the User_ID does not match up with that of
    the administrator, the request does not succeed.
    '''
    group = Group.query.filter_by(code_name=group_code_name)
    db_session.delete(group)
    db_session.commit()
    return True


def edit_group(group_code_name, request):
    '''
    INPUT
    A filled-out GroupForm which validates.  Essentially, the edit uses the same
    view as the create.  It allows you to update the description, by-line, and
    display name.
    '''
    # Grab object we're changing
    group = Group.query.filter_by(code_name = group_code_name)

    # Grab new values from form
    new_name = request.form['human-name']
    new_byline = request.form['by-line']
    new_desc = request.form['description']

    # Modify the object
    group.human_name = new_name
    group.byline = new_byline
    group.description = new_desc

    # Commit our changes to the session
    db_session.commit()
    return True