__author__ = 'John'

from flask import Flask, request, session, g, redirect, url_for,\
     abort, render_template, flash, make_response
from flask.ext.login import current_user, login_required
import groupbot
from groupbot import app
from groupbot.models import Group, Task, Event
import groupbot.helper as helper
import groupbot.forms as forms
import groupbot.controllers as controllers

@app.route('/group/create', methods=['GET', 'POST'])
def group_create():
    form = forms.GroupForm(request.form)
    if form.validate_on_submit():
        successful_create = controllers.group.create(request)
        if successful_create == True:
            flash("You successfully created a group called {}!".format(form.code_name), 'success')
            return redirect(url_for(group_detail, group_code_name=form.code_name))
        else:
            flash("Something went wrong when you tried to create the Group!  Sorry :(")
    return render_template('templates/pages/groups/create.html', form=form)

@app.route('/dashboard')
def group_list():
    '''
    View which combines a list of quick summaries concerning the goings-on
    for each of your groups.
    '''
    # First, grab all of the User's Groups via the list of their Memberships.
    groups = helper.get_groups_from_user(current_user)

    # Then get the relevant information from each group and puts it into the content object
    content = {"groups":[]}
    for group in groups:
        content['groups'].append({'human_name':group.human_name,
                      'code_name':group.code_name,
                      'byline':group.byline,
                      'description':group.description})

    # Lastly, pass in the "infonav" object used to build the sidebar navigation.
    infonav = groupbot.views.build_infonav('user')
    return render_template('pages/groups/list.html', content=content, infonav=infonav)


@app.route('/group/<group_code_name>')
def group_detail(group_code_name):
    '''
    In-depth view of the recent activity of the group, including everything
    pertaining to the specific member viewing it.  The group can mark
    specific content as public and viewable by anonymous members if it so
    chooses (think of it like combining your management and your publicity
    into the same activity).
    '''

    # First, grab us a Group, fill in its info, make the content object, and build the infonav
    group = Group.query.filter_by(code_name = group_code_name)
    content = {}
    content['group_name'] = group.human_name
    content['group_byline'] = group.byline
    content['group_code_name'] = group.code_name
    infonav = groupbot.views.build_infonav('group', current_group=group)

    # Now, get all the information and endpoints required to build up the Tasks component of the view
    tasks = group.tasks.order_by(Task.deadline).limit(5)
    tasks_view = []
    for each_task in tasks:
        tasks_view.append({
            'name':each_task.name,
            'task_id':each_task.task_id,
            'description':each_task.description,
            'deadline':str(each_task.deadline),
            'delivered':each_task.delivered
        })
    content['tasks'] = tasks_view

    # Next up, play the same game but with the Group's events.
    events = group.events.order_by(Event.start_time).limit(5)
    events_view = []
    for each_event in events:
        events_view.append({
            'name':each_event.name,
            'event_id':each_event.event_id,
            'description':each_event.description,
            'start_time':str(each_event.start_time),
            'end_time':str(each_event.end_time)
        })
    content['events'] = events_view

    # Last but not least, generate all of the information required to populate the list of Members down
    # at the bottom of the page.
    members = group.members
    members_view = []
    for each_member in members:
        members_view.append({
            'name':each_member.name,
            'photo':each_member.photo,
            'roles':[{'name':role.name, 'role_id':role.role_id} for role in each_member.roles]
        })
    content['members'] = members_view

    # With all that said and done, return that motherfucker.
    return render_template('pages/groups/detail.html', content=content, infonav=infonav)

@app.route('/group/<group_codename>/edit', methods=['GET', 'POST'])
def group_edit(group_codename):
    current_group = Group.query.filter_by(group_code_name=group_codename).firs()
    form = forms.GroupForm(request.form)
    form.human_name = current_group.human_name
    form.code_name = current_group.code_name
    form.byline = current_group.byline
    form.description = current_group.description

    if form.validate_on_submit():
        successful_edit = controllers.group.edit_group(group_codename, request)
        if successful_edit:
            flash("You successfully edited {0}!".format(current_group.code_name), 'success')
            return redirect(url_for(group_detail, group_code_name=group_codename))
    else:
        return render_template('pages/groups/edit.html', form=form)

@app.route('/group/<group_code_name>/delete', methods=['GET', 'POST'])
def group_delete(group_code_name):
    content = {'group_code_name':group_code_name}
    form = forms.DeleteForm(request.form)
    if form.validate_on_submit():
        if form.delete == True:
            successful_delete = controllers.group.delete_group(group_code_name)
            if successful_delete:
                flash('You successfully deleted {0}.'.format(group_code_name))
                return redirect(url_for(group_list))
            else:
                return redirect(url_for(group_detail, group_code_name=group_code_name))
    else:
        return render_template('pages/groups/delete.html', content=content)