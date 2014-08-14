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
# Atomic Events for ROLES.
#----------------------------------------------------------------------------#
def create_role(request):
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
    group_id = int(request.POST['group_id'])
    role_name = request.form['name']
    description = request.form['description'] if request.form['description'] else None
    member = int(request.form['member']) if request.form['member'] else None
    new_role = Role(group_id = group_id, name = role_name, \
                                description = description, member_id = member)
    db_session.add(new_role)
    db_session.commit()
    return True

def delete_role(request):
    '''
    INPUT
    Takes a Role_ID to be deleted.

    OUTPUT
    Removes the Role's row from the database.  It is therefore no longer associated
    with any members.  If there are any Tasks only approved by that Role, then the
    approval responsibilities move to the people who were last holding said Role.
    '''
    group_id = int(request.POST['group_id'])
    group = Group.query.get(group_id)
    role_id = int(request.POST['role_id'])
    role = Role.query.get(role_id)
    if role.group_id == group_id:
        db_session.delete(role)
        db_session.commit()
    return True

# Gives a Role to a specific Member
def assign_role(request):
    '''
    INPUT
    Takes a Group_ID, Role_ID, and Member_ID.

    OUTPUT
    Adds the Member to the Member_ID propety of the specified Role in the
    specified Group.  If the Member is already assigned to the Role, throws an
    Exception saying that Role was already assigned to that Member.
    '''
    # Get IDs from the request
    group_id = int(request.POST['group_id'])
    role_id = int(request.POST['role_id'])
    member_id = int(request.POST['member_id'])

    # Grab the actual Role & Member objects using the provided IDs.
    group = Group.query.get(group_id)
    role = Role.query.get(role_id)
    member = Member.query.get(member_id)

    # Next, run a sanity check to make sure that Role is part of the Member's Group
    if role not in group.roles:
        raise Exception("This Role isn't a part of that Group, it can't go to that Member!")

    # Finally, add the Member to the Role's Role.member_id property and commit.
    role.member_id.append(member)
    db_session.add(role)
    db_session.commit()
    return True

def remove_role(request):
    '''
    INPUT
    Takes a Group_ID, Role_ID, and Member_ID.

    OUTPUT
    Removes the specified Member from the specified Role's Member_ID
    relation.  If the Member was not actually in that relation, throws an
    Exception saying the specified Member did not have that Role.
    '''
    group_id = int(request.POST['group_id'])
    role_id = int(request.POST['role_id'])

    group = Group.query.get(group_id)
    role = Role.query.get(role_id)

    if role not in group.roles:
        raise Exception("This Role isn't a part of that Group to begin with!")
    else:
        db_session.delete(role)
        db_session.commit()
        flash("The '{0}' was deleted from the '{1}' group.".format(role.name, group.human_name))
    return True