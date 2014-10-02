__author__ = 'John'

from flask import Flask, request, session, g, redirect, url_for,\
     abort, render_template, flash, make_response
from flask.ext.login import current_user
from groupbot import app
import groupbot as gbot
from groupbot.models import Member, Group, Role, User
import groupbot.forms as forms
import groupbot.controllers as controllers

@app.route('/group/<group_codename>/members/add', methods=['GET', 'POST'])
def member_add(group_codename):
    '''
    This is the view where people can invite other users into the Group.  After all, the Group's
    kind of a joke if it doesn't have any members.
    :param group_codename:
    :return:
    '''

    # First, get the page up and ready to go, build the form and infonav.
    this_group = Group.query.filter_by(codename = group_codename).first()
    infonav = gbot.views.build_infonav('group', current_group=this_group)
    form = forms.MemberInviteForm()

    # If the form's been submitted, check and see if the

    return render_template('templates/pages/members/add.html', form=form, infonav=infonav)

@app.route('/group/<group_codename>/members')
def member_list(group_codename):
    '''
    This thing gives you a view of all the Members in the Group.  Their names, photos, and bios
    are listed, and each listing is a link to the detail page for that Member.

    :param group_codename:
    :return:
    '''

    # First, grab the group, build the infonav, and add the standard properties to content.
    this_group = Group.query.filter_by(codename = group_codename).first()
    infonav = gbot.views.build_infonav('group', current_group=this_group)
    content = {
        'group_name':group_codename,
        'members':[]
    }

    # Then, build up the list of dicts describing each Member
    for each_member in this_group.members:
        content['members'].append({
            'realname':each_member.get_realname(),
            'codename':each_member.codename,
            'bio':each_member.bio,
            'photo_url':each_member.photo
        })

    # With all that said and done, return this bad boy and stop worrying about it.
    return render_template('templates/pages/members/list.html', content=content, infonav=infonav)

@app.route('/group/<group_codename>/members/<member_codename>')
def member_detail(group_codename, member_codename):
    '''
    This view gives the proverbial skinny on a Member.  What's their name, bio, photo?
    It also shows the Roles they hold, the Tasks on their plate, and the Events they're
    invited to.  Yay for transparency!

    :param group_codename:
    :param member_codename:
    :return:
    '''

    # First, grab the group, member, and user, as well as build up the navbar.
    (this_group, this_member) = gbot.views.get_group_and_member(group_codename, member_codename)
    infonav = gbot.views.build_infonav('group', current_group=this_group)

    # Next, build the parts of content that only require a one-liner -- names, photo, and roles.
    content = {'realname':this_member.get_realname(),
               'codename':this_member.codename,
               'group_name':group_codename,
               'user_id':this_member.user_id,
               'photo':this_member.photo,
               'roles':[{'name':each_role.name, 'role_id':each_role.role_id} for each_role in this_member.roles],
               'tasks':[],
               'events':[]}

    # Now for the mildly more involved part, putting together the dicts for the Tasks and Events.
    for each_task in this_member.doing_tasks:
        content['tasks'].append({
            'name':each_task.name,
            'task_id':each_task.task_id,
            'description':each_task.description,
            'deadline':str(each_task.deadline),
            'delivered':each_task.delivered,
            'late':each_task.is_late()
        })

    # Note that we check whether or not the Event has happened before assigning an 'attended' value...
    for each_event in this_member.events:
        event_dict = {
            'name':each_event.name,
            'event_id':each_event.event_id,
            'description':each_event.description,
            'start_time':str(each_event.start_time),
            'end_time':str(each_event.end_time),
            'rsvp':each_event.rsvp
        }
        if each_event.already_happened():
            event_dict['attended'] = each_event.attended_by(this_member)
        content['events'].append(event_dict)

    # With all that said and done, we're good to return and show the page.
    return render_template('templates/pages/members/detail.html', content=content, infonav=infonav)

@app.route('/group/<group_codename>/members/<member_codename>/edit', methods=['GET', 'POST'])
def member_edit(group_codename, member_codename):
    '''
    This page lets you modify the information specific to a Member.  Namely, the codename
    within the group, bio, and photo.

    :param group_codename:
    :param member_codename:
    :return:
    '''

    # First, make sure that this is a person trying to edit one of their own Memberships
    this_group = Group.query.filter_by(codename=group_codename).first()
    this_member = Member.query.filter_by(group_id=this_group.id, codename=member_codename).first()
    if this_member.user_id == current_user.user_id:

        # Assuming it is, populate the Edit form.
        form = forms.MemberEditForm()
        form.codename = this_member.codename
        form.bio = this_member.bio
        form.photo = this_member.photo

        if form.validate_on_submit():
            # Send them back to Group view if it's a successful edit
            try:
                new_codename = str(request.form['codename'])
                controllers.member.edit_member(this_member.member_id, request)
                flash("Score!  You just successfully edited your Membership, " + new_codename)
                return redirect(url_for(gbot.views.member.member_detail(group_codename, new_codename)))

            # Let them know what went wrong if it wasn't
            except Exception as e:
                flash("Dang, that edit didn't work...  Check it out: " + str(e))
                return redirect(url_for(gbot.views.member.member_edit(group_codename, member_codename)))

        # If they haven't submitted, though, just show 'em the dang page!
        return render_template('templates/pages/members/edit.html', form=form)

    # If it ain't, punt them back out to the top level view.
    else:
        flash("You can't edit that Member profile, it isn't yours!", "error")
        return redirect(url_for(gbot.views.group.group_list()))


@app.route('/group/<group_codename>/members/<member_codename>/delete', methods=['GET', 'POST'])
def member_delete(group_codename, member_codename):
    this_group = Group.query.filter_by(codename = group_codename).first()
    this_member = Member.query.filter_by(group_id = this_group.group_id, codename=member_codename).first()
    current_member = Member.query.filter_by(group_id = this_group.group_id, user_id = current_user.user_id).first()

    # First, make sure the Member is a part of the Group they're deleting a Member from.  Note, we want to
    # support somebody else deleting a Member, so the Member doing the deleting doesn't necessarily have to
    # be the Member being deleted.
    if this_member.group_id == current_member.group_id:

        # Assuming they're valid, populate the page and make the form.
        content = {'member_id':int(this_member.member_id)}
        form = forms.SignedDeleteForm()

        if form.validate_on_submit():

            # If their submission and signature check out, delete the Member.
            if form.signature_field.signature == current_user.codename:
                try:
                    flash("Okay, you just removed {0} from {1}.  Sorry to see them go!".format(this_member.codename, this_group.codename))
                    controllers.member.remove_member(this_member.member_id)
                    return redirect(url_for(gbot.views.group.group_list()))
                except Exception as e:
                    flash("Huh, that didn't work for some reason.  The magic computer says: " + str(e))
                    return redirect(url_for(gbot.views.member.member_delete(group_codename, member_codename)))

            # Otherwise, say their signature didn't check out and we couldn't delete the Member.
            else:
                flash("Not to be a jerk or anything, but you didn't sign your name right...  Are you sure you signed the User codename, not the Member one?")
                return redirect(url_for(gbot.views.member.member_delete(group_codename, member_codename)))

        # If they haven't submitted yet, just show 'em the delete page.
        return render_template('templates/pages/members/delete.html', form=form, content=content, current_member=current_member)

    # If they're not even part of the Group, get 'em outta there.
    else:
        flash("What are you doing trying to delete a Member from " + str(this_group.codename) + "? You don't even go here!", "error")
        return redirect(url_for(gbot.views.group.group_list()))