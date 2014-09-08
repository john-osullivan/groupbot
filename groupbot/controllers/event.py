__author__ = 'John'

import datetime
from flask import Flask, request, session, g, redirect, url_for,\
     abort, render_template, flash, make_response
from flask.ext.sqlalchemy import SQLAlchemy,Pagination
from groupbot import app
from flask.ext.login import current_user
from models import db_session, User, Group, Member, \
                                Role, Task, Bond, \
                                Event, User, Infopage,\
                                Infoblock
from controllers import get_group_member

#----------------------------------------------------------------------------#
# Atomic Events for EVENTS
#----------------------------------------------------------------------------#
def create_event(request, group_id):
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

    # Grab the mandatory parameters out of the form
    name = request.form['name']
    start_time = datetime.new(request.form['start_time'])
    location = request.form['location']
    visible_to_uninvited = request.form['visible_to_uninvited']
    invited_can_invite = request.form['invited_can_invite']

    # Get the list of host Members and Roles
    host_members = [Member.query.filter_by(codename=membername, group_id=group_id).first()
                    for membername in request.form['host_members']]
    host_roles = [Role.query.get(int(role_id)) for role_id in request.form['host_roles']]

    # Grab the two optional parameters.
    end_time = request.form['end_time'] if request.form['end_time'] != "" else None
    description = request.form['description'] if request.form['description'] != "" else None

    # Make a new object, set its parameters which aren't handled by the init function.
    new_event = Event(name=name, group_id=group_id, start_time=start_time, end_time=end_time,
                      description=description, location=location, visible_to_uninvited=visible_to_uninvited,
                      invited_can_invite=invited_can_invite)
    new_event.hosting_members.extend(host_members)
    new_event.hosting_roles.extend(host_roles)
    new_event.update_hosts_by_roles()

    # Sanity check: the Event still has at least one host, right?
    if len(new_event.hosting_members) == 0:
        raise Exception("Event '"+str(new_event.name) + "' doesn't have any host members!  That's not right.")

    # Since that Exception wasn't triggered, we're good to save our work and be done.
    db_session.add(new_event)
    db_session.commit()


def delete_event(request, event_id):
    '''
    INPUT
    Member object in the request to validate Permissions.  Other than that, the event_id
    is enough.

    RESULT
    If all goes well, event is deleted and returns True.  Otherwise, an Exception.
    '''

    # If they want it deleted...
    if request.form['delete'] == True:
        # Grab the specified Event
        event = Event.query.get(event_id)

        # Delete it and save our work.
        db_session.delete(event)
        db_session.commit()


def edit_event(request, event_id):
    '''
    INPUT
    Member object in the request to check permissions.  Also an Event form in order to
    update the contents of this one.

    RESULT
    If all goes well, event is edited and returns True.  Otherwise, an Exception.
    '''

    # First, grab the event and its group.
    this_event = Event.query.get(event_id)
    this_group = Group.query.get(this_event.group_id)

    # Now, use the form parameters to update the Event.
    this_event.name = request.form['name']
    this_event.start_time = request.form['start_time']
    this_event.end_time = request.form['end_time']
    this_event.location = request.form['location']
    this_event.description = request.form['description']
    this_event.visible_to_uninvited = request.form['visible_to_uninvited']
    this_event.invited_can_invite = request.form['invited_can_invite']

    # Nope, need to actively update both the hosting Roles and hosting Members.  Then call a function on
    # the Event class, update_hosts_by_roles(), which updates the Members whenever the Roles change.
    this_event.hosting_members = [Member.query.get(member_id) for member_id in request['host_members']]
    new_hosting_roles = [Role.query.get(role_id) for role_id in request.form['host_roles']]
    if new_hosting_roles != this_event.hosting_roles:
        this_event.hosting_roles = new_hosting_roles
        this_event.update_hosts_by_roles()

    db_session.add(this_event)
    db_session.commit()


def event_invite(request, event_id):
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
    this_event = Event.query.get(event_id)
    inviting_member = Member.query.filter_by(user_id=current_user.user_id, group_id=this_event.group_id).first()
    # Check to make sure the inviting Member is a host.
    if this_event.is_host(inviting_member):

        # First, we need to update the Members who are invited.  The form field returns a list of codenames.
        this_event.invited_members = [Member.query.filter_by(group_id=this_event.group_id, codename=membername).first()
                                      for membername in request.form['invited_members']]

        # Next, check if the invited Roles need updating.  If the values are updated, make sure to call
        # the Event's update_invited_members_after_role_change() function. The current behavior is that
        # changing the Roles will reset the Member invitations to be accurate with the change -- No Exceptions.
        new_roles = [Role.query.get(role_id) for role_id in request.form['invited_roles']]
        if new_roles != this_event.invited_roles:
            this_event.update_invited_by_roles()

        db_session.add(this_event)
        db_session.commit()
    else:
        raise Exception("That Member can't invite someone, they're not a host!")


def event_rsvp(request, event_id, member_id):
    '''
    INPUT
    Member object in the request to make sure they were invited to begin with. Other
    than that, the event_id is enough to work things out.

    RESULT
    The Member is added to the Event's .rsvp_yes attribute.  The function returns
    True to confirm successful operation, Exception if it fails.
    '''
    # Grab the standard Group and Member so we know who and where the request is coming from.

    # Grab the event and validate where the guest was even invited.
    # ...
    # Because *God*, does she even go here?
    this_event = Event.query.get(event_id)
    rsvp_member = Member.query.get(member_id)
    if rsvp_member in this_event.invited:
        attending = request.form['attending']
        if attending: # Note, this works specifically because the form's value for Yes is True.
            this_event.rsvp_yes.append(rsvp_member)
        else:
            this_event.rsvp_no.append(rsvp_member)
        db_session.commit()
    else:
        return Exception("That member wasn't even invited to this event!")

def event_attend(request, event_id):
    '''
    INPUT
    Need a Member object in the request, representing the Member who attended.  This may not
    be the Member who calls the function, so it's important to make sure we're putting the
    right Member's information in.  Other than that, we're good with event_id.

    RESULT
    Member is added to the Event's .attended_yes attribute.  Same success:True,
    failure:Exception behavior as elsewhere.
    '''

    this_event = Event.query.get(event_id)
    for each_member in this_event.invited_members:
        if (each_member.codename in request.form.attended) and (each_member not in this_event.attended):
            this_event.attended.append(each_member)
        elif (each_member.codename not in request.form.attended) and (each_member in this_event.attended):
            this_event.attended.remove(each_member)
    db_session.add(this_event)
    db_session.commit()
    return this_event