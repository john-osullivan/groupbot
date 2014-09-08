__author__ = 'John'

from flask import Flask, request, session, g, redirect, url_for,\
     abort, render_template, flash, make_response
from flask.ext.sqlalchemy import SQLAlchemy,Pagination
from groupbot import app
from models import db_session, User, Group, Member, \
                                Role, Task, Bond, \
                                Event, User, Infopage,\
                                Infoblock
import datetime

#----------------------------------------------------------------------------#
# Atomic Events for TASKS.
#----------------------------------------------------------------------------#
def create_task(request, group_id):
    '''
    INPUT
    Takes in a submission of the create task form, gathering the Title,
    Description, Deadline, Assignee, and optional Points arguments.  Also takes
    the Group ID and Assigner ID implicitly from the page request.

    OUTPUT
    Creates a new Task entry in the database associated with all relevant
    parties, adding it to the Tasks for each Member assigned.
    '''

    # Grab the information of the creator group & member

    # Grab the basic stuff associated with the Task.  When's it due, what is it, what has to be returned,
    # any special comments.
    name = request.form['name']
    deadline = request.form['deadline'] if request.form['deadline'] != None else None
    description = request.form['description'] if request.form['description'] != None else None
    deliverable = request.form['deliverable'] if request.form['deliverable'] != None else None
    comments = request.form['comments'] if request.form['comments'] != None else None

    # Create the task using the information we picked out of the form.
    new_task = Task(name=name, group_id=group_id, description=description, deadline=deadline,
                    deliverable=deliverable, comments=comments)

    # Now we need to set all our ForeignKey associations.  First, make lists of all the Members and Roles
    # which are supposed to be true now.
    new_approving_members = [Member.query.filter_by(group_id=group_id, codename=membername)
                             for membername in request.form['approving_members']]
    new_delivering_members = [Member.query.filter_by(group_id, codename=membername)
                              for membername in request.form['delivering_members']]

    new_approving_roles = [Role.query.get(int(role_id)) for role_id in request.form['approving_roles']]
    new_delivering_roles = [Role.query.get(int(role_id)) for role_id in request.form['delivering_roles']]

    # Then, set all of these relations to be set as described by the form.
    new_task.approving_members = new_approving_members
    new_task.approving_roles = new_approving_roles
    new_task.delivering_members = new_delivering_members
    new_task.delivering_roles = new_delivering_roles

    # Finally, correct the approving_members and delivering_members relations to only contain Members
    # who have one of the Roles specified in the approving_roles and delivering_roles relations.
    new_task.update_approvers_by_roles()
    new_task.update_deliverers_by_roles()

    # Add and save our work.
    db_session.add(new_task)
    db_session.commit()
    return new_task

def edit_task(task_id, request):
    '''
    INPUT
    Uses the task_id to get the Task object, uses any updated parameters from the form
    to change its attributes.  Assumes, as always, that the group_id and member_id are
    coming through the request.

    RESULT
    The Task is updated in the database -- what did you think was going to happen?  True
    if success, Exception if not.
    '''
    # Grab the task we're talking about
    task = Task.query.get(task_id)

    # Grab any new values (other than Member selections) from the form, choose the old ones if the form
    # field wasn't updated.
    new_name = request.form['name'] if request.form['name'] != task.name else task.name
    new_desc = request.form['description'] if request.form['description'] != task.description else task.description
    new_deliverable = request.form['deliverable'] if request.form['deliverable'] != task.deliverable else task.deliverable
    new_deadline = request.form['deadline'] if request.form['deadline'] != task.deadline else task.deadline
    new_comments = request.form['comments'] if request.form['comments'] != task.comments else task.comments

    # Modify the Task to fit our new values.
    task.name = new_name
    task.description = new_desc
    task.deliverable = new_deliverable
    task.deadline = new_deadline
    task.comments = new_comments

    # Now, build up the lists of delivering & approving Members as described by the form.
    new_delivering_members = [Member.query.filter_by(group_id=task.group_id, codename=membername).first()
                      for membername in request.form['delivering_members']]
    new_approving_members = [Member.query.filter_by(group_id=task.group_id, codename=membername).first()
                     for membername in request.form['approving_members']]
    new_delivering_roles = [Role.query.get(int(role_id)) for role_id in request.form['delivering_roles']]
    new_approving_roles = [Role.query.get(int(role_id)) for role_id in request.form['approving_roles']]

    # Then update the database record and call our update_xxxx_by_role functions.
    task.delivering_members = new_delivering_members
    task.delivering_roles = new_delivering_roles
    task.approving_members = new_approving_members
    task.approving_roles = new_approving_roles
    task.update_approvers_by_roles()
    task.update_deliverers_by_roles()

    # Sanity check -- there's at least one approving_member, right?
    if len(task.approving_members) > 0:

        # No need to add, since the object already exists in the database!  Just commit.
        db_session.commit()
        return task

    else:
        # Oh shit, not a single approving Member?  The Task will flounder and die!  Throw an Exception.
        raise Exception("Task #"+task.task_id+" is being saved without any approving_members!")


def delete_task(task_id, member_id):
    '''
    INPUT
    Triggered via a close button element, handed the task_id implicitly from the
    page request.  Assumes there will be a member_id and group_id in the request.

    REQUIREMENT
    Can only be used before a task has been delivered.

    OUTPUT
    Removes a Task entry from the database, erasing it from the Tasks of each
    Member.
    '''

    # Grab the Task we need.
    task = Task.query.get(task_id)
    member = Member.query.get(member_id)

    # Sanity check -- does this Member have delete rights -- i.e. are they an approving member?
    if task.is_approving(member):
        # Yup!  Delete it and save our work.
        db_session.delete(task)
        db_session.commit()

    else:
        # No!  Scoundrels, throw up an Exception.
        raise Exception("This Member is trying to delete a Task they aren't approving!")

# Used to deliver tasks.
def deliver_task(request, task_id, member_id):
    '''
    INPUT
    Triggered via a delivery mechanism.  Only requires the task_id and a reference
    to the deliverable which completed it.  If an already delivered task is delivered
    again, the new deliverable overwrites the old one.  Assumes that request.POST['deliverable']
    has something in it -- text, image, file, whatever.  For now, it's stored as binary data.

    OUTPUT
    Changes the delivered Boolean of the specified Task to True, puts whatever was stored at
    that part of the request into the Task.deliverable attribute.
    '''
    current_member = Member.query.get(member_id)
    task = Task.query.get(task_id)
    signature = request.form['signature']
    if task.is_delivering(current_member):
        if current_member.get_realname() == signature:
            task.delivered = True

            # Set the late property to True if they turned it in after the deadline.
            if datetime.now() > task.deadline:
                task.late = True

            db_session.commit()
        else:
            raise Exception("The signature doesn't line up the Member's stored real name!")
    else:
        raise Exception("The person turning this in isn't the one who was supposed to!")

def approve_task(request, task_id, member_id):
    '''
    INPUT
    Requires the task_id and the ID of the request submitter.  Checks to make
    sure the person approving the task is one of the people who assigned it.

    OUTPUT
    Changes the approved boolean of the task to True.
    '''
    approving_member = Member.query.get(member_id)
    this_task = Task.query.get(task_id)
    if this_task.is_approving(approving_member):
        if approving_member.get_realname() == request.form['signature']:
            this_task.approved = True
            db_session.commit()
        else:
            raise Exception("The provided signature doesn't match up with the Member's real name!")
    else:
        raise Exception("The person submitting this approval isn't an approving Member!")