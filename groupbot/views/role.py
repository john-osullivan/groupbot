__author__ = 'John'

from flask import Flask, request, session, g, redirect, url_for,\
     abort, render_template, flash, make_response
from flask.ext.login import current_user
from groupbot import app
from groupbot.models import db_session, User, Group, Member, \
                                member_roles, Role, member_tasks, Task, \
                                Event
import groupbot as gbot
import groupbot.forms
import groupbot.controllers
import groupbot.views

@app.route('/group/<group_codename>/roles/create')
def role_create(group_codename):
    '''
    This is the view where a Member of a Group can create a new Role.

    :param group_codename:
    :return:
    '''

    # Grab the Group, Member, and build the nav
    (current_group, current_member) = gbot.views.group_and_member_from_user_and_groupname(current_user.user_id, group_codename)
    infonav = gbot.views.build_infonav('group', current_group=current_group)

    # For the record, make sure that the person trying to make a Role is actually a Member of the Group.
    if current_member != None:

        # Now that we know they are, build that form.
        form = gbot.forms.RoleForm()

        # If that form's been submitted...
        if form.validate_on_submit():
            # Have the controller create the object, flash a success, and show 'em all the Roles.
            try:
                new_role = gbot.controllers.role.create_role(current_group.group_id, request)
                flash("Nice!  You just made a Role called " + str(new_role.name) + "!", "success")
                return redirect(url_for(role_list, group_codename=group_codename))

            # Unless -- heaven forbid -- something went WRONG!  Then tell 'em what it was.
            except Exception as e:
                flash("Damn!  Something just got screwy, couldn't make that Role.  Here's the deal: " + str(e), "error")
                return redirect(url_for(role_create, group_codename=group_codename))

        # If it ain't been submitted, that's it -- just show 'em the page.
        return render_template('templates/pages/roles/create.html', infonav=infonav, form=form)

    # If we get to here, this isn't even being done by a Group Member!  Punt 'em out.
    else:
        flash("You're not part of that Group, you can't make up a Role!  Get outta there.", "error")
        return redirect(url_for(gbot.views.group.group_list))

@app.route('/group/<group_codename>/roles/')
def role_list(group_codename):
    '''
    This spits out a list of all the Roles in a Group with the key information associated.
    Also, LIST COMPREHENSIONS.  This content object is technically a one-line nested list
    comprehension.  Just spaced out for clarity.
    '''

    # First, get the group so we can build the navbar -- as always.
    (this_group, infonav) = gbot.views.get_group_and_nav(group_codename)
    all_roles = this_group.roles
    content = [{                                # This is a list of the information for each role
        'role_id':each_role.role_id,
        'name':each_role.name,
        'members':[{                            # which includes a list of members with each.
                       'member_id':each_member.member_id,
                       'name':each_member.name,
                   } for each_member in each_role.members]
    } for each_role in all_roles]
    return render_template('templates/pages/roles/list.html', infonav=infonav, content=content)

@app.route('/group/<group_codename>/roles/<role_id>')
def role_detail(group_codename, role_id):
    '''
    A complete view of all the information relevant to a role.  This would include
    all Tasks given to or from the Role, all Events hosted with its permission,
    a link to its Info, and a list of all Members who are performing it.  Additionally
    it would have links
    '''

    # First, get the group and infonav.
    (this_group, infonav) = gbot.views.get_group_and_nav(group_codename)
    this_role = Role.query.get(role_id)

    # Then, start building up the content object.  The Role's name and description are easy
    # one-liners.  Note, the description is going to support some Markdown wiki shit -- that'll
    # actually turn into the documentation...
    content = {'name':this_role.name,
               'description':this_role.description,
               'members':[],
               'events':[],
               'tasks':[]}

    # For these lists of things, make a list comprehension.  We drag it out over lines to not fuck wit' PEP8.
    content['members'] = [{'id':each_member.member_id,
                           'name':each_member.get_realname()
                          } for each_member in this_role.members]

    content['events'] = [{'id':each_event.event_id,
                          'name':each_event.name}
                        for each_event in this_role.events]

    content['tasks'] = [{'id':each_task.task_id,
                         'name':each_task.name}
                        for each_task in this_role.tasks]

    return render_template('templates/pages/roles/detail.html', infonav=infonav, content=content)

@app.route('/group/<group_codename>/roles/<role_id>/edit')
def role_edit(group_codename, role_id):
    '''
    This view lets Members edit the Roles in their Groups.  Specifically, it lets them update
    the name, description, and subset of Members holding the Role.  CALL DAT CONTROLLER FUNCTION.
    '''

    # First, grab our Group, Member, and build the infonav.
    (this_group, this_member) = gbot.views.group_and_member_from_user_and_groupname(current_user.user_id, group_codename)
    infonav = gbot.views.build_infonav('group', current_group=this_group)

    # For a sanity check, make sure this User is actually a Member of the Group.
    if this_member != None:

        # If they are, build the form.  Since this is an edit, we need to fill in form values.
        form = gbot.forms.RoleForm()
        this_role = Role.query.get(role_id)
        form.name = this_role.name
        form.description = this_role.description

        # Populating the selection field is a bit of a bitch.  I need to specify all possible Members
        # with their IDs, then specify which IDs should be selected.  For style points, the selected
        # ones should go first in the list.  However, I DON'T HAVE INTERNET AND CAN'T CHECK THE
        # MOTHERFUCKING DOCUMENTATION.  I should really save it locally.  For now, I think this
        # list comprehension will at least populate the choices.
        form.members = [(member.id, member.get_realname()) for member in this_group.members]

        # Now, if the form's been submitted, get our controller game up.
        if form.validate_on_submit():

            # If all goes well, flash 'em a new message and send 'em to the edited role's detail page.
            try:
                edited_role = gbot.controllers.role.edit_role(role_id, request)
                flash("Awww yeah, you just edited the Role called " + edited_role.name + " -- good for you.", "success")
                return redirect(url_for(role_detail, group_codename=group_codename, role_id=role_id))

            # But, y'know, shit happens.  If shit happened, tell 'em what it was.
            except Exception as e:
                flash("We have some tragic news -- the edit failed.  Here's what went down: " + str(e), "error")
                return redirect((url_for(role_edit, group_codename=group_codename, role_id=role_id)))

        # If nothing's been submitted, we're done -- show 'em the page.
        return render_template('templates/pages/roles/edit.html', infonav=infonav, form=form)

    # If we got here, they weren't a Member of the Group whose Role they were trying to edit!  PUNT 'EM.
    else:
        flash("WHOA.  You're not even part of this Group, man.  What're you doing editing its Roles?", "error")
        return redirect(url_for(gbot.views.group.group_list, infonav=infonav))

@app.route('/group/<group_codename>/roles/<role_id>/delete')
def role_delete(group_codename, role_id):
    '''
    Simple enough, this is just the confirmation page to delete a Role.  Are they SURE they wanna delete that?
    '''

    # First, grab our Group, Member, and build the infonav.
    (this_group, this_member) = gbot.views.group_and_member_from_user_and_groupname(current_user.user_id, group_codename)
    infonav = gbot.views.build_infonav('group', current_group=this_group)

    # SANITY CHECK!  Is this User even a Member of the Group?
    if this_member != None:

        # Okay, they're good to make the operation -- build the form.
        form = gbot.forms.DeleteForm()

        # If they've submitted the form...
        if form.validate_on_submit():
            role_name = Role.query.get(int(role_id)).name

            # Pass the request to the controller function, who checks the value in the form to see if the
            # delete was supposed to happen.  Depending on the outcome, flash a different message.
            try:
                deleted = gbot.controllers.role.delete_role(role_id, request)
                if deleted:
                    flash("You just deleted the Role named " + role_name + ".")
                    return redirect(url_for(gbot.views.role.role_list, group_codename=group_codename))
                else:
                    flash(role_name + " wasn't deleted -- phew.")
                    return redirect(url_for(gbot.views.role.role_detail, group_codename=group_codename, role_id=role_id))

            # Unless, of course, something entirely different goes wrong.  Then tell 'em the story.
            except Exception as e:
                flash("Whoa, something isn't right -- the delete failed!  Here's the skinny: " + str(e))
                return redirect(url_for(gbot.views.role.role_detail, group_codename=group_codename, role_id=role_id))

        # If they haven't submitted it, we're good -- just show 'em the page.
        else:
            return render_template('templates/pages/roles/delete.html', form=form, infonav=infonav)
    # AH HA!  I knew we weren't crazy.  This User shouldn't modify this Role, they're not part of the Group!
    else:
        flash("Hold up, you're not part of this Group -- you can't delete a Role!", "error")
        return redirect(url_for(gbot.views.group.group_list))
