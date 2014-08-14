__author__ = 'John'

from flask import Flask, request, session, g, redirect, url_for,\
     abort, render_template, flash, make_response
from flask.ext.sqlalchemy import SQLAlchemy,Pagination
from app import app
from models import db_session, User, Group, Member, \
                                Role, Task, Bond, \
                                Event, User, Infopage,\
                                Infoblock
from controller import get_group_member

#----------------------------------------------------------------------------#
# Atomic Events for MEMBERS.
#----------------------------------------------------------------------------#
def add_member(group_code_name, request):
    '''
    INPUT
    A group ID, a user ID, and a Member Form which only has one (optional)
    argument of a Preferred Name.  Letting people decide who they are based
    on where they are is generally a nice thing.

    OUTPUT
    Create a new Member row associated with the User and Group, possibly
    holding a value for Preferred Name.  The Role and Task relations are
    empty by default.
    '''
    group_id = request.POST['group_id']
    group = Group.query.get(group_id)
    pref_name = request.form['preferred_name'] if request.form['preferred_name'] else None
    new_member = Member(group_id=group_id, preferred_name=pref_name)
    return True

def edit_member(member_id, request):
    '''
    INPUT
    A Member ID whose profile is being edited, a validated MemberForm to update
    their information.

    RESULT
    Updates the Member's information, returns True if successful and throws an
    Exception if it wasn't.
    '''
    member = Member.query.get(member_id)
    new_name = request.form['preferred_name']
    member.preferred_name = new_name
    return True

def remove_member(member_id, request):
    '''
    INPUT
    A  Member ID for the member to be removed.

    OUTPUT
    Removes the specified Member's row from the database, removing them
    from all Roles they were assigned to.  If a Task was only assigned to them,
    it is removed as well.
    '''
    member_id = request.POST['member_id']
    group_id = request.POST['group_id']
    member = Member.query.get(member_id)
    group = Group.query.get(group_id)
    db_session.delete(member)
    db_session.commit()
    return True