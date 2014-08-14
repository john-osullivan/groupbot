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
# Atomic Events for EVENTS
#----------------------------------------------------------------------------#
def create_event(request):
    '''
    INPUT
    Member object in the request to make sure Permissions are valid.  Also a filled
    out EventCreate form.

    REQUIRES
    Member object in the request.

    RESULT
    If all goes well, event is created and returns True.  Otherwise, an Exception.
    '''
    # Grab the standard Group and Member so we know who and where the request is coming from.
    group_id = request.POST['group_id']
    member_id = request.POST['member_id']

    # Grab the mandatory parameters out of the form
    name = request.form['name']
    host_id = request.form['host']
    start_time = request.form['start_time']
    location = request.form['location']

    # Grab the two optional parameters.
    end_time = request.form['end_time'] if request.form['end_time'] != "" else None
    description = request.form['description'] if request.form['description'] != "" else None

    # Make a new object, set its parameters which aren't handled by the init function.
    new_event = Event(name, group_id, start_time, end_time, host_id, description)
    db_session.add(new_event)
    db_session.commit()


def delete_event(request):
    '''
    INPUT
    Member object in the request to validate Permissions.  Other than that, the event_id
    is enough.

    RESULT
    If all goes well, event is deleted and returns True.  Otherwise, an Exception.
    '''
    # Grab the standard Group and Member so we know who and where the request is coming from.
    group_id = request.POST['group_id']
    member_id = request.POST['member_id']

    # Grab the specified Event
    event = Event.query.get(request.POST['event_id'])

    # Delete it and save our work.
    db_session.delete(event)
    db_session.commit()


def edit_event(request):
    '''
    INPUT
    Member object in the request to check permissions.  Also an Event form in order to
    update the contents of this one.

    RESULT
    If all goes well, event is edited and returns True.  Otherwise, an Exception.
    '''
    # First, grab the Group and Member creating the InfoPage to do some validation.
    (group, member) = get_group_member(request)

    # Next, the event.
    event = Event.query.get(request.POST['event_id'])

    # Check if each parameter was updated, grab the valid version (updated or still in database)
    if request.POST['updated']:
        event.name = request.form['name']
        event.host_id = request.form['host_id']
        event.start_time = request.form['start_time']
        event.end_time = request.form['end_time']
        event.location = request.form['location']
        event.description = request.form['description']
        db_session.commit()


def event_invite(request):
    '''
    INPUT
    There needs to be a member object in the request, but this is not the Member being invited.
    The Member in the request is the User doing the inviting, and needs to be verified to make
    sure they have Permission to invite people.  The Member being invited is contained in
    request.form['member'].  The event, of course, comes from the URL.

    RESULT
    The specified Member is added to the Event's 'invited' relationship.  It returns True if
    everything goes the same way.
    '''
    # Grab the standard Group and Member so we know who and where the request is coming from.
    (group, inviting_member) = get_group_member(request)
    event = Event.query.get(request.POST['event_id'])

    # Check to make sure the inviting Member is a host.
    if inviting_member in event.host:

        # Grab the Member who was invited and add them to the invited relation.
        invited_member = Member.query.get(request.form['member'])
        event.invited.append(invited_member)
        db_session.commit()
    else:
        raise Exception("That Member can't invite someone, they're not a host!")


def event_rsvp(request):
    '''
    INPUT
    Member object in the request to make sure they were invited to begin with. Other
    than that, the event_id is enough to work things out.

    RESULT
    The Member is added to the Event's .rsvp_yes attribute.  The function returns
    True to confirm successful operation, Exception if it fails.
    '''
    # Grab the standard Group and Member so we know who and where the request is coming from.
    (group, rsvp_member) = get_group_member(request)

    # Grab the event and validate where the guest was even invited.
    # ...
    # Because *God*, does she even go here?
    event = Event.query.get(request.POST['event_id'])
    if rsvp_member in event.invited:
        attending = request.form['attending']
        if attending: # Note, this works specifically because the form's value for Yes is True.
            event.rsvp_yes.append(rsvp_member)
        else:
            event.rsvp_no.append(rsvp_member)
        db_session.commit()
    else:
        return Exception("That member wasn't even invited to this event!")

def event_attend(request):
    '''
    INPUT
    Need a Member object in the request, representing the Member who attended.  This may not
    be the Member who calls the function, so it's important to make sure we're putting the
    right Member's information in.  Other than that, we're good with event_id.

    RESULT
    Member is added to the Event's .attended_yes attribute.  Same success:True,
    failure:Exception behavior as elsewhere.
    '''
    # First, grab the Group and Member creating the InfoPage to do some validation.
    (group, member) = get_group_member(request)

    group_id = request.POST['group_id']
    attend_member = Member.query.get(int(request.form['member']))
    event = Event.query.get(int(request.form['event']))
    if attend_member in event.invited:
        attended = request.form['attended']
        if attended:
            event.attended_yes.append(attend_member)
        else:
            event.attended_no.append(attend_member)
        db_session.commit()
        return True
    else:
        return Exception("That Member wasn't invited to begin with!")