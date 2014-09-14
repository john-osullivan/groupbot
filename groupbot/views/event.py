__author__ = 'John'

from flask import Flask, request, session, g, redirect, url_for,\
     abort, render_template, flash, make_response
from flask.ext.login import current_user
from groupbot import app
import groupbot as gbot
import groupbot.forms
import groupbot.controllers as controllers
from groupbot.models import User, Group, Member, Role, Task, Event

@app.route('/group/<group_codename>/events')
def event_list(group_codename):
    '''
    This gives Users a broad overview of all the upcoming Events in their Group.  It goes through each
    Event, checks if the Member would have the ability to view it, and then gives them a quick burst of
    information about it.
    '''

    # First up, build the infonav, get the Group, get the Member.
    (infonav, this_group) = gbot.views.get_context(group_codename=group_codename)
    this_member = Member.query.filter_by(group_id=this_group.group_id, user_id=current_user.user_id).first()

    # Now, we need to start building up content.  Let's iterate through all the possible Events...
    content={'events':[]}
    for each_event in this_group.events:

        # First, check if the Member is supposed to be able to see this Event.  Are they connected to it, or is it visible?
        if each_event.member_can_see(this_member):

            # If it is, put in the constant parameters of the Event.
            event_dict = {
                'name':each_event.name,
                'start_time':str(each_event.start_time),
                'end_time':str(each_event.end_time),
                'location':each_event.location,
                'invited_count':len(each_event.invited),
            }

            # Then, check if the Event has already happened and add that information in.  If it hasn't
            # happened yet, put in the RSVP counts.  If it's already happened, put in the attendance counts.
            if each_event.already_happened():
                event_dict['happened'] = True
                event_dict['attended_count'] = len(each_event.attended)
                event_dict['missed_count'] = event_dict['invited_count'] - event_dict['attended_count']
            else:
                event_dict['happened'] = False
                event_dict['yes_count'] = len(each_event.rsvp_yes)
                event_dict['no_count'] = len(each_event.rsvp_no)

            # Append that bitch to the greater dictionary and then we're done!
            content['events'].append(event_dict)

    return render_template('templates/pages/events/list.html', infonav=infonav, content=content)

@app.route('/group/<group_codename>/events/create', methods=['GET', 'POST'])
def event_create(group_codename):
    '''
    Instantiates the form used to create an Event, letting Members set the new Event's name, start_time,
    end_time, location, description, hosting_members, and hosting_roles.

    :param group_codename:
    :return redirect to event_detail:
    '''

    # First, build up the infonav, get the Group object and the current member.
    (infonav, this_group) = gbot.views.get_context(group_codename=group_codename)
    current_member = gbot.views.get_current_member(group_codename=group_codename, current_user=current_user)

    # Sanity check: is this actually a Member of the Group?
    if current_member is not None:

        # Now that we know we're dealing with a Group Member, build up the form and pass it into the view.
        form = gbot.forms.EventForm()

        # If nobody's submitted yet, just show 'em the page with the nav and form.
        if not form.validate_on_submit():
            return render_template('pages/events/create.html', infonav=infonav, form=form)

        # If somebody has, call the controller function, flash the appropriate message, and move the Member along.
        else:
            try:
                new_event = controllers.event.create_event(request, this_group.group_id, current_member.member_id)
                flash("Heck yeah!  You just made a new Event called " + form.name + ", way to go.", "success")
                return redirect(url_for(gbot.views.event.event_detail, group_codename=group_codename, event_id=new_event))
            except Exception as e:
                flash("Oh VanDerShnootzle, the Event create didn't work!  Here's the dealio: " + str(e), "error")
                return redirect(url_for(gbot.views.event.event_create, group_codename=group_codename))

    else:
        # Ah ha, that sneaky punk.  Flash 'em a warning and punt 'em out!
        flash("Excuse me, but I'm going to have to ask you to leave that page -- you're not in the Group!", "warning")
        return redirect(url_for(gbot.views.group.group_list))

@app.route('/group/<group_codename>/events/<int:event_id>')
def event_detail(group_codename, event_id):
    '''
    A complete view of all information relevant to an event, aka the detail view.
    This would include the host, start time, end time, description, and summary of RSVP and attendance.
    Note, it first checks if the Member is allowed to view this event at all.
    '''

    # First, build up the infonav and get the group and event objects.
    (infonav, this_group, this_event) = gbot.views.get_context(group_codename=group_codename, event_id=event_id)

    # Check and see if the Member viewing the Event is allowed to do that.
    current_member = Member.query.filter_by(group_codename=group_codename, user_id=current_user.user_id).first()
    if this_event.member_can_see(current_member):

        # Now that we know they can, start building up all the one-liners in the content block,
        # and make empty lists for the others.
        content = {
            'groupname':this_group.codename,
            'name':this_event.name,
            'description':this_event.description,
            'start_time':str(this_event.start_time),
            'end_time':str(this_event.end_time),
            'location':str(this_event.location),
            'host':this_event.is_host(current_member),
            'happened':this_event.already_happened(),
            'invited':this_event.is_invited(current_member),
            'can_invite':this_event.can_invite(current_member),
        }

        # If there's attendance to report on, report that thang -- report it.
        # READ: Make the lists of member identity dictionaries for each spots.
        if this_event.already_happened():
            content['attendance']['attended'] = [{'name':each_member.get_realname(), 'id':each_member.member_id} for each_member in this_event.attended]
            content['attendance']['absent'] = [{'name':each_member.get_realname(), 'id':each_member.member_id} for each_member in this_event.get_noshows()]

        # Next, make the identity dictionaries for the Members hosting the Event
        content['hosts'] = [each_member.get_identity() for each_member in this_event.hosts]

        # Now we add in the information determining everyone's RSVP.  Note, we don't list people in "Invited" once
        # they've RSVPd.  It's more reporting the status of what you said you'd do.
        content['rsvp']['yes'] = [each_member.get_identity() for each_member in this_event.rsvp_yes]
        content['rsvp']['no'] = [each_member.get_identity() for each_member in this_event.rsvp_no]
        content['rsvp']['none'] = [each_member.get_identity() for each_member in this_event.no_rsvp()]

        # With all that done, return the page for the Member to see!
        return render_template('pages/events/detail.html', infonav=infonav, content=content)

    # WHOA -- this person can't see that event!  Send 'em back to the Events page.
    else:
        flash("Eh, not to be a jerk, but you're technically not allowed to see that.  Sorry!", "error")
        return redirect(url_for(gbot.views.event.event_list, group_codename=group_codename))

@app.route('/group/<group_codename>/events/<int:event_id>/edit')
def event_edit(group_codename, event_id):
    '''
    This view lets the host of an event (AND ONLY THE HOST) change the name, hosts, description, location,
    start_time, end_time, visible_to_uninvited, and invited_can_invite of an Event.  It's a standard
    take the form and call the controller function kind of thing.  It DOES NOT allow for inviting
    new Members/Roles to the Event, it does not handle RSVP-ing to an Event, it does not handle taking
    attendance at an Event.
    '''

    # First, grab the context, build the infonav, and get the Member who's looking at this.
    (infonav, this_group, this_event) = gbot.views.get_context(group_codename=group_codename, event_id=event_id)
    current_member = gbot.views.get_current_member(group_codename, current_user)

    # Now, safety check.  Is the Member one of the Event's hosts?
    if this_event.is_host(current_member):

        # Now that we know they are, build the form to show 'em, populating it with all the current Event info.
        form = gbot.forms.EventForm()

        # First, all the easy one-liners.  Not hosts, really.
        form.name.default = this_event.name
        form.start_time.default = this_event.start_time
        form.end_time.default = this_event.end_time
        form.location.default = this_event.location
        form.description.default = this_event.description

        # Now, set the member_codenames and member_realnames for the host_members field.  Note that we need to process
        # it for the actual information to update.
        form.host_members.choices = [(each_member.get_identity()['codename'], each_member.get_identity()['realname'])
                              for each_member in this_group.members]
        form.host_members.default = [each_member.get_identity()['codename'] for each_member in this_event.hosts]
        form.host_members.process()

        # Next, set the role_names and role_id for the host_roles field.  Again, process the field when we're done.
        form.host_roles.choices = [(each_role.role_id, each_role.name) for each_role in this_group.roles]
        form.host_roles.default = [each_role.role_id for each_role in this_event.hosting_roles]
        form.host_roles.process()

        # Now, what happens if the form was submitted and we have new info?  CONTROLLER TIME.
        if form.validate_on_submit():

            # Try and perform the edit, flash a success, and send 'em back to the detail.
            try:
                controllers.event.edit_event(request, event_id)
                flash("You just edited the " + str(this_event.name) + " event!  Nice.", "success")
                return redirect(url_for(gbot.views.event.event_detail, group_codename=group_codename, event_id=event_id))

            # Unless shit went wrong, in which case say so.
            except Exception as e:
                flash("Yikes!  The edit failed for some reason, sorry.  Here's why: " + str(e), "error")
                return redirect(url_for(gbot.views.event.event_edit, group_codename=group_codename, event_id=event_id))

        # With that done, if nothing's been submitted, we're good to return the form!
        return render_template('pages/events/edit.html', infonav=infonav, form=form)
    # Well I'll be damned, they're trying to edit this Event when they're not a host!  PUNT!
    else:
        flash("Uhh, you're not supposed to be there.  Editing an Event that you aren't hosting -- tomfoolery!", "error")
        return redirect(url_for(gbot.views.event.event_detail, group_codename=group_codename, event_id=event_id))


@app.route('/group/<group_codename>/events/<int:event_id>/delete')
def event_delete(group_codename, event_id):
    '''
    This page essentially confirms whether or not the current_member (who must be a host) REALLY wants to
    delete the event.
    '''

    # First, build the infonav, grab the context, and the current Member, and build the form.
    (infonav, this_group, this_event) = gbot.views.get_context(group_codename=group_codename, event_id=event_id)
    current_member = gbot.views.get_current_member(group_codename, current_user)

    # Now, make sure that the current_member is a host and can actually delete the Event.
    if this_event.is_host(current_member):
        form = gbot.forms.DeleteForm()
        content = {'event_name':this_event.name}

        # If they submit the form...
        if form.validate_on_submit():

            # If they wanna do it, call that controller function.
            if form.delete == True:
                # If all goes well, flash 'em a success and send 'em back to the Event list.
                try:
                    controllers.event.delete_event(request,event_id)
                    flash("You successfully cancelled the Event called " + str(this_event.name) + ".", "success")
                    return redirect(url_for(gbot.views.event.event_list, group_codename=group_codename))
                # Tell 'em what happened if something goes wrong.
                except Exception as e:
                    flash("Oof, something just went wrong.  Sorry about that.  Check this out: " + str(e))
                    return redirect(url_for(gbot.views.event.event_list, group_codename=group_codename))
            # If they didn't wanna do it, tell 'em we kept it safe and it's still there.  Show 'em the details.
            else:
                flash("Okay, " + str(this_event.name) + " is still happening!")
                return redirect(url_for(gbot.views.event.event_detail, group_codename=group_codename, event_id=event_id))

        # If the form hasn't been submitted yet, though, then just show 'em the page.
        else:
            return render_template('pages/events/delete.html', infonav=infonav, form=form, content=content)

@app.route('/group/<group_codename>/events/<int:event_id>/invite')
def event_invite(group_codename, event_id):
    '''
    This displays the form to invite Group Members and Roles, as well as calling the controller functions
    to actually make the underlying data change.

    :param group_codename:
    :param event_id:
    :return:
    '''

    # First, grab the infonav, group, event, and current Member.
    (infonav, this_group, this_event) = gbot.views.get_context(group_codename=group_codename, event_id=event_id)
    current_member = gbot.views.get_current_member(group_codename, current_user)

    # Check if the Member can invite people to the Event.
    if this_event.can_invite(current_member):

        # If they can, create and populate the form.  Set the possible choices and already invited Members.
        form = gbot.forms.EventInviteForm()

        # Populated all the options for the Roles and all the actually chosen ones.
        form.invited_roles.choices = [(each_role.role_id, each_role.name) for each_role in this_group.roles]
        form.invited_roles.default = [each_role.role_id for each_role in this_event.invited_roles]
        form.invited_roles.process()

        # Do the same thing for the Member field.
        form.invited_members.choices = [(each_member.codename, each_member.get_realname())
                                        for each_member in this_group.members]
        form.invited_members.default = [each_member.codename for each_member in this_event.invited_members]
        form.invited_members.process()
    return render_template('pages/events/invite.html', infonav=infonav, form=form)

@app.route('/group/<group_codename>/events/<event_id>/rsvp')
def event_rsvp(group_codename, event_id):
    '''
    This page displays the form to let invited Members RSVP to the Event.

    :param group_codename:
    :param event_id:
    :return:
    '''

    # First, grab the group, event, and current member.
    (infonav, this_group, this_event) = gbot.views.get_context(group_codename=group_codename, event_id=event_id)
    current_member = gbot.views.get_current_member(this_group.codename, current_user)

    # Sanity check -- is the Member invited?
    if this_event.is_invited(current_member):

        # Assuming they are, build the form and populate it with the current value.
        form = gbot.forms.EventRSVPForm()

        # Check the RSVP fields...
        if current_member in this_event.rsvp_yes:
            form.attending.default = True

        elif current_member in this_event.rsvp_no:
            form.attending.default = False

        form.attending.process()

        # If the form's been submitted, use the controller function.
        if form.validate_on_submit():

            # Try to run the RSVP controller function, flash a success, and return to list.
            try:
                controllers.event.event_rsvp(request, event_id, current_member.member_id)
                flash("Nice, thanks for RSVPing to " + this_event.name + "!", "success")
                return redirect(url_for(gbot.views.event.event_list, group_codename=group_codename))

            # Unless, god forbid, something goes wrong.  Then say so and return to RSVP.
            except Exception as e:
                flash("Dang, that RSVP didn't work.  Here's the angry computer print-out: " + str(e))
                return redirect(url_for(gbot.views.event.event_rsvp, group_codename=group_codename, event_id=event_id))

        # If the RSVP hasn't been made yet, just show 'em the form.
        return render_template('pages/events/rsvp.html', infonav=infonav, form=form)

    # If the current_member isn't actually invited, bounce 'em out to the Event list for weirdness.
    else:
        flash("Uh, you're not invited to that.  You can't RSVP!", "error")
        return redirect(url_for(gbot.views.event.event_list, group_codename=group_codename))

@app.route('/group/<group_codename>/events/<event_id>/attendance')
def event_attendance(group_codename, event_id):
    '''
    This page displays the form to let any of the Event's hosts (AND ONLY THOSE HOSTS) take attendance.
    It has to handle a few different states -- specifically, before and after attendance is taken for the
    first time, and whether or not the current_member is a host.

    If the Event is visible_to_uninvited, then anyone in the Group can see the Attendance.  If it isn't, then
    those invited to the meeting can see the attendance.  The only people who can ever edit the Attendance
    are the hosts of the Event.

    :param group_codename:
    :param event_id:
    :return:
    '''

    # Quickly get the infonav built, grab the context, and get the Member for validation.
    (infonav, this_group, this_event) = gbot.views.get_context(group_codename=group_codename, event_id=event_id)
    current_member = gbot.views.get_current_member(group_codename=group_codename,current_user=current_user)

    # First off, let's prep the content object.  We need to say whether or not it exists, then make it if it does.
    content = {'event':{'name':this_event.name,
                        'id':this_event.id},
               'is_host':this_event.is_host(current_member),
               'attendance_taken':this_event.attendance_taken(),
               'groupname':group_codename}

    # Now, let's see if attendance has been taken.  No need to build the attendance object if there's nothing to show!
    if this_event.attendance_taken():
        content['attendance_record'] = [{
                                            'realname':each_member.get_identity()['realname'],
                                            'codename':each_member.get_identity()['codename'],
                                            'attended':this_event.attended_by(each_member)
                                         } for each_member in this_event.invited_members]

    # If the Member's a host, we need to build the form with the current information and show it.  Also do
    # the processing once the form is submitted.
    if this_event.is_host(current_member):

        # Build the form and check if it just got submitted.
        form = gbot.forms.EventAttendanceForm()
        if form.validate_on_submit:
            # If it DID, then call the controller function to update the attendance and send the Member
            # back to look at it with a redirect.
            try:
                controllers.event.event_attend(request, this_event.id)
                flash("Hey, you just updated the attendance list for " + this_event.name + " -- nice!", "success")
                return redirect(url_for(gbot.views.event.event_attendance, group_codename=group_codename, event_id=event_id))
            except Exception as e:
                flash("Oof, that change of attendance didn't work -- sorry!  Here's the problem: " + str(e), "error")
                return redirect(url_for(gbot.views.event.event_attendance, group_codename=group_codename, event_id=event_id))
        else:
            # If it didn't, set the choices with the invited Members.
            form.attended.choices = [(each_member.codename, each_member.get_realname())
                                     for each_member in this_event.invited_members]

            # If attendance exists, fill in the default values.
            if this_event.attendance_taken():
                form.attended.default = [each_member.codename for each_member in this_event.attended]

            # With the form modified, just process it and return the template with everything we've made.
            form.attended.process()
            return render_template('pages/events/attendance.html', infonav=infonav, content=content,
                                   form=form)

    # If the Member isn't a host, but the Attendance is visible or they're invited, show 'em what we'd already made.
    elif (this_event.is_invited(current_member)) or (this_event.visible_to_uninvited):
        return render_template('pages/events/attendance.html', infonav=infonav, content=content)

    # If they don't have any reason to check this Attendance, get 'em out of there!
    else:
        flash("Sorry, but you can't check the attendance for that Event :(  Maybe ask the hosts?", "error")
        return redirect(url_for(gbot.views.event.event_list, group_codename=group_codename))
