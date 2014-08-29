__author__ = 'John'

from flask import Flask, request, session, g, redirect, url_for,\
     abort, render_template, flash, make_response
from flask.ext.sqlalchemy import SQLAlchemy,Pagination
from app import app
from models import db_session, Group, Member, User

#----------------------------------------------------------------------------#
# Atomic Events for MEMBERS.
#----------------------------------------------------------------------------#
def add_member(group_codename, request):
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
    group = Group.query.filter_by(codename=group_codename)
    user_codename = request.form['user_codename'] if request.form['user_codename'] else None
    user_email = request.form['user_email'] if request.form['user_email'] else None
    user = User.query.filter_by(codename = user_codename, email = user_email).first()
    new_member = Member(group_id=group.group_id, user_id=user.user_id, codename=user_codename)
    db_session.add(new_member)
    db_session.commit()
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
    new_codename = request.form['codename']
    new_bio = request.form['bio']
    new_photo = request.form['photo']
    member.codename = new_codename
    member.bio = new_bio
    member.photo = new_photo
    db_session.commit()
    return True

def remove_member(member_id):
    '''
    INPUT
    A  Member ID for the member to be removed.

    OUTPUT
    Removes the specified Member's row from the database, removing them
    from all Roles they were assigned to.  If a Task was only assigned to them,
    it is removed as well.
    '''
    member = Member.query.get(member_id)
    db_session.delete(member)
    db_session.commit()
    return True