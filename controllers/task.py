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
# Atomic Events for TASKS.
#----------------------------------------------------------------------------#
def create_task(request):
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
    group_id = request.POST['group_id']
    giver_member_id = request.POST['member_id']

    # Grab the mandatory information associated with the task
    name = request.form['name']
    doer_member_id = request.POST['doing_member']

    # Grab the optional information associated with the task
    parent_id = request.form['parent_id'] if request.form['parent_id'] != None else None
    deadline = request.form['deadline'] if request.form['deadline'] != None else None
    description = request.form['description'] if request.form['description'] != None else None
    comments = request.form['comments'] if request.form['comments'] != None else None

    # Create the task and set its optional parameters
    new_task = Task(name, doer_member_id, giver_member_id, group_id)
    new_task.deadline = deadline
    new_task.description = description
    new_task.comments = comments
    new_task.parent = Task.query.get(parent_id)

    # Add and save our work.
    db_session.add(new_task)
    db_session.commit()
    return True

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
    task = Task.query.get(request.POST['task_id'])

    # Grab any new values from the form, choose the old ones if the form field wasn't updated.
    new_name = request.form['name'] if request.form['name'] != task.name else task.name
    new_desc = request.form['description'] if request.form['description'] != task.description else task.description
    new_doing_member = request.form['doing_member'] if request.form['doing_member'] != task.doing_member else task.doing_member
    new_deadline = request.form['deadline'] if request.form['deadline'] != task.deadline else task.deadline
    new_comments = request.form['comments'] if request.form['comments'] != task.comments else task.comments

    # Modify the Task to fit our new values.
    task.name = new_name
    task.description = new_desc
    task.doing_member = new_doing_member
    task.deadline = new_deadline
    task.comments = new_comments

    # No need to add, since the object already exists in the database!
    db_session.commit()
    return True


def delete_task(request):
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
    # Grab the Group, Member, and Task we need.
    group = Group.query.get(request.POST['group_id'])
    member = Member.query.get(request.POST['member_id'])
    task = Task.query.get(request.POST['task_id'])

    # Make sure the Task and Member are both part of the Group.
    if ((task.group_id == group.id) and (task.giving_id == member.id)):
        # Then delete the object from the database and save the change.
        db_session.delete(task)
        db_session.commit()
        return True
    else:
        raise Exception("Either the Task wasn't part of the given group, or you weren't!")

# Used to deliver tasks.
def deliver_task(request):
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
    group = Group.query.get(request.POST['group_id'])
    delivering_member = Group.query.get(request.POST['member_id'])
    task = Task.query.get(request.POST['task_id'])
    deliverable = request.POST['deliverable']
    if (task.doing_member == delivering_member):
        task.delivered = True
        task.deliverable = deliverable
        db_session.commit()
        return True
    else:
        raise Exception("The person turning this in isn't the one who was supposed to!")

def approve_task(request):
    '''
    INPUT
    Requires the task_id and the ID of the request submitter.  Checks to make
    sure the person approving the task is one of the people who assigned it.

    OUTPUT
    Changes the approved boolean of the task to True.
    '''
    approving_member = Group.query.get(request.POST['member_id'])
    task = Task.query.get(request.POST['task_id'])
    if (task.giving_id == approving_member.member_id):
        task.approved = True
        db_session.commit()
        return True
    else:
        raise Exception("The person submitting this approval isn't the one who was supposed to!")