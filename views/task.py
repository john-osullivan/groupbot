__author__ = 'John'

from flask import Flask, request, session, g, redirect, url_for,\
     abort, render_template, flash, make_response
from app import app
from flask.ext.login import current_user
from models import User, Group, Member, Role, Task, Event
import views
import controllers
import forms


@app.route('/group/<group_codename>/tasks')
def task_list(group_codename):
    '''
    Creates the content object required to fill out the Task list page.  Need the name and assigned
    Member (or Members, since there's no other way) for each Task, as well as True or False values
    for 'delivered', 'late', and 'approved'.
    '''

    # First off, get the group, nav, and Member.
    (infonav, this_group) = views.get_context(groupcode_name=group_codename)
    current_member = views.get_current_member(group_codename=group_codename, current_user=current_user)

    # Sanity check: is the current_member real, somebody in the Group?
    if current_member is not None:

        # Okay, now that we know they're really in the Group, let's build the content object.
        content = {'groupname':group_codename,
                   'tasks':[]}
        for each_task in this_group.tasks:
            content['tasks'].append({'name':each_task.name,
                         'id':each_task.task_id,
                         'delivering_members':[each_member.get_identity() for each_member in each_task.delivering_members],
                         'deadline':str(each_task.deadline),
                         'delivered':each_task.delivered,
                         'late':each_task.late,
                         'approved':each_task.approved
                         })

        # With all that said, all we gotta do is show 'em the page!
        return render_template('templates/pages/tasks/list.html', infonav=infonav, content=content)
    else:
        # AH HA!  We weren't crazy, this is an impostor!  Punt 'em out to group_list with a warning.
        flash("What?!  You're not in " + this_group.codename + ", you can't see its Tasks!", "error")
        return redirect(url_for(views.group.group_list))

@app.route('/group/<group_codename>/tasks/new', methods=['GET', 'POST'])
def task_create(group_codename):
    '''
    Presents the user with the form to create a new Task, calls the controller function once the Member
    submits the form.

    :param group_codename:
    :return:
    '''

    # First up, grab the infonav, group, and current_member.
    (infonav, this_group) = views.get_context(group_codename=group_codename)
    current_member = views.get_current_member(group_codename=group_codename, current_user=current_user)

    # SANITY CHECK: Is the Member in the Group?
    if current_member is not None:

        # Okay, they're good to get started.  Build up the form with all the standard elements.
        form = forms.TaskForm()

        # Now, populate the SelectMultiple Boxes for choosing Members and Roles.  Make sure to set the
        # current_member as part of the default list of approving members!
        form.delivering_roles.choices = [(each_role.role_id, each_role.name) for each_role in this_group.roles]
        form.approving_roles.choices = [(each_role.role_id, each_role.name) for each_role in this_group.roles]
        form.delivering_members.choices = views.get_select_list_for_members(this_group.members)
        form.approving_members.choices = views.get_select_list_for_members(this_group.members)
        form.approving_members.default = [current_member.codename]
        form.delivering_roles.process()
        form.approving_roles.process()
        form.delivering_members.process()
        form.approving_members.process()

        # Assuming nobody's submitted this bad boy yet, just show 'em the page!
        if not form.validate_on_submit():
            return render_template('templates/pages/tasks/create.html', infonav=infonav, form=form)

        # However, if they have, we call the controller function, flash messages, and redirect to the detail view.
        else:
            new_task = controllers.task.create_task(request, this_group.group_id)
            flash("Nice!  You just made a new Task called " + new_task.name + ", good on you.", "success")
            return redirect(url_for(views.task.task_detail, group_codename=group_codename, task_id=new_task.task_id))

    else:
        # AH HA, NOT CRAZY.  They're not supposed to be here, punt 'em.
        flash("Hey, you can't be there!  You're not a Member of that Group!", "error")
        return redirect(url_for(views.group.group_list))

@app.route('/group/<group_codename>/tasks/<int:task_id>')
def task_detail(group_codename, task_id):
    '''
    A complete view of all information relevant to a task, aka the detail view.
    This would include giving, do-er, deliverable, deadline, description, approval
    status.
    '''

    # First, get the infonav, group, and task -- as well as the current member for a sanity check.
    (infonav, this_group, this_task) = views.get_context(group_codename=group_codename, task_id=task_id)
    current_member = views.get_current_member(group_codename=group_codename, current_user=current_user)

    # Now, perform the check of our sanity: is the user a Member in this group?
    if current_member is not None:

        # Okay, they're not an impostor.  Let's build the content object.  Everything is a one-liner because
        # of list comprehensions and helper methods.  It's pretty hot, man.
        content = {'groupname':group_codename,
                   'name':this_task.name,
                   'id':this_task.task_id,
                   'approving_roles':[{'id':each_role.role_id, 'name':each_role.name} for each_role in this_task.approving_roles],
                   'approving_members':[each_member.get_identity() for each_member in this_task.approving_members],
                   'delivering_roles':[{'id':each_role.role_id, 'name':each_role.name} for each_role in this_task.delivering_roles],
                   'delivering_members':[each_member.get_identity() for each_member in this_task.delivering_members],
                   'description':this_task.description,
                   'comments':this_task.comments,
                   'deadline':this_task.deadline,
                   'deliverable':this_task.deliverable,
                   'delivered':this_task.delivered,
                   'late':this_task.is_late(),
                   'approved':this_task.approved,
                   'is_delivering':this_task.is_delivering(current_member),
                   'is_approving':this_task.is_approving(current_member)
        }

        # See?  Define one dictionary and all we gotta do now is return the information.
        return render_template('templates/pages/tasks/detail.html', infonav=infonav, content=content)
    else:
        # EGAD!  They were an impostor, not worthy to be here!  Throw an error message and punt 'em out.
        flash("Sorry, I can't let you see that, " + current_member.codename +" -- you're not part of that Group!", "error")
        return redirect(url_for(views.group.group_list))



@app.route('/group/<group_codename>/tasks/<int:task_id>/edit', methods=['GET','POST'])
def task_edit(group_codename, task_id):
    '''
    Populates the form which allows current Approvers of a Task to edit it.  They can add other Approvers,
    change the name/description/deadline/deliverable/comments, as well as add more Deliverers.  When it
    '''

    # First off, grab the group, task, infonav, and current_member.
    (infonav, this_group, this_task) = views.get_context(group_codename=group_codename, task_id=task_id)
    current_member = views.get_current_member(group_codename=group_codename, current_user=current_user)

    # Sanity check -- is the editing Member one of the Task's approving Members?  Gotta make sure.
    if this_task.is_approving(current_member):

        # Now that we know they're good, build the form up and populate it with the existing data.
        form = forms.TaskForm()
        form.name = this_task.name
        form.description = this_task.description
        form.deliverable = this_task.deliverable
        form.deadline = form.deadline
        form.comments = form.comments

        # Now we need to populate the Member and Role SelectFields, both the choices and defaults.

        # First all the choices...
        form.approving_members.choices = views.get_select_list_for_members(this_group.members)
        form.delivering_members.choices = views.get_select_list_for_members(this_group.members)
        form.approving_roles.choices = [(each_role.role_id, each_role.name) for each_role in this_group.roles]
        form.delivering_roles.choices = [(each_role.role_id, each_role.name) for each_role in this_group.roles]

        # Then with all the default values...
        form.approving_members.default = [list_option['codename'] for list_option in
                                          views.get_select_list_for_members(this_task.approving_members)]
        form.delivering_members.default = [list_option['codename'] for list_option in
                                          views.get_select_list_for_members(this_task.delivering_members)]
        form.approving_roles.default = [role.role_id for role in this_task.approving_roles]
        form.delivering_roles.default = [role.role_id for role in this_task.delivering_roles]


        # Then process all those fields we just modified!
        form.delivering_members.process()
        form.delivering_roles.process()
        form.approving_members.process()
        form.approving_roles.process()

        # Assuming nobody has submitted anything by now, show people the page.
        if not form.validate_on_submit():
            return render_template('templates/pages/tasks/edit.html', infonav=infonav, form=form)
        else:
            # But oh god help us, somebody did.  Somebody done submitted the form.  Call the controller function,
            # flash some appropriate-ass messages, and give 'em that good old redirect.
            try:
                controllers.task.edit_task(task_id, request)
                flash("Nice -- you just successfully edited the Task called " + str(form.name) + "!", "success")
                return redirect(url_for(views.task.task_detail, group_codename=group_codename, task_id=task_id))
            except Exception as e:
                flash("Oh shoot, that edit didn't go right.  Here's the deal: " + str(e), "error")
                return redirect(url_for(views.task.task_edit, group_codename=group_codename, task_id=task_id))
    else:
        # Ah ha!  I knew we weren't crazy!  They can't edit this, punt them out to the detail view.
        flash("WHOA -- you can't edit this Task, you're not even part of the Group!", "warning")
        return redirect(url_for(views.group.group_list))


@app.route('/group/<group_codename>/tasks/<int:task_id>/delete', methods=['GET','POST'])
def task_delete(group_codename, task_id):
    '''
    Populates the Task Delete page with valid content, checks the form submission to see if we should
    follow through and actually delete the selected Task.
    '''

    # First off, grab our infonav, group, task, and current_member.
    (infonav, this_group, this_task) = views.get_context(group_codename=group_codename, task_id=task_id)
    current_member = views.get_current_member(group_codename=group_codename, current_user=current_user)

    # Sanity check: is the current_member approving this task?  If not, they shouldn't even be able
    # to see this screen!
    if this_task.is_approving(current_member):

        # Ah, okay, these guys are good.  In that case, build their form and content object.
        form = forms.DeleteForm()
        content = {'task_name':this_task.name}

        # If nothing's been submitted, just show 'em the page!
        if not form.validate_on_submit():
            return render_template('templates/pages/tasks/delete.html', infonav=infonav, form=form, content=content)

        # However, if something DOES get submitted, check the form to see if they want it gone.  Then do what it says.
        else:
            if form.delete:
                # Shit, they did it.  Call the controller, flash the appropriate result message, send 'em along.
                task_name = this_task.name
                try:
                    controllers.task.delete_task(this_task.task_id)
                    flash("Okay, you just deleted the Task called " +task_name +".", "success")
                    return redirect(url_for(views.task.task_list, group_codename=group_codename))
                except Exception as e:
                    flash("Whoa, we couldn't delete the Task called " + this_task.name + "!  Check it out: " + str(e), "error")
                    return redirect(url_for(views.task.task_delete, group_codename=group_codename, task_id=this_task.task_id))
            else:
                # They didn't delete it.  Flash 'em a message saying so, send 'em back to the detail page.
                flash("Phew, the Task wasn't deleted.")
                return redirect(url_for(views.task.task_detail, group_codename=group_codename, task_id=task_id))
    else:
        # Ah ha!  It's been a sham all along, they can't be here.  Punt them to the detail view.
        flash("Whoa there, you can't delete that Task!  Only an approving Member can delete it.", "error")
        return redirect(url_for(views.task.task_detail, group_codename=group_codename, task_id=task_id))

@app.route('/group/<group_codename>/tasks/<int:task_id>/deliver', methods=['GET','POST'])
def task_deliver(group_codename, task_id):
    '''
    Displays the form required to deliver a Task, calls the deliver_task controller function once the
    Member actually submits the form to try and deliver.  Sanity checks to make sure the Member trying
    to deliver the Task was a delivering_member to begin with.

    :param group_codename:
    :param task_id:
    :return:
    '''

    # First up, grab the infonav, this_group, this_task, and the current_member... for sanity.
    (infonav, this_group, this_task) = views.get_context(group_codename=group_codename, task_id=task_id)
    current_member = views.get_current_member(group_codename=group_codename, current_user=current_user)

    # Sanity check: is this a delivering Member?
    if this_task.is_delivering(current_member):

        # Okay, not crazy.  Build up the delivery form, along with any page content we'll need.
        form = forms.TaskDeliverForm()
        content = {'task_name':this_task.name,
                   'deliverable':this_task.deliverable,
                   'deadline':this_task.deadline}

        # If the form ain't been submitted, just show 'em the page!
        if not form.validate_on_submit():
            return render_template('templates/pages/tasks/deliver.html', group_codename=group_codename, task_id=task_id)

        # Unless it has, in which case call up the controller function, flash the appropriate message, and redirect.
        else:
            try:
                controllers.task.deliver_task(request, this_task.task_id, current_member.member_id)
                flash("Nice, you delivered the Task called " + this_task.name +".  Good on you!", "success")
                return redirect(url_for(views.task.task_detail, group_codename=group_codename, task_id=task_id))
            except Exception as e:
                flash("Oh dang, that delivery went all wrong!  Here's the skinny: " + str(e), "error")
                return redirect(url_for(views.task.task_deliver, group_codename=group_codename, task_id=task_id))
    else:
        # I'M NOT CRAZY, HE SHOULDN'T BE HERE.  Flash a message, punt a Member.
        flash("Hey, you can deliver that Task -- you're not a delivering Member!", "error")
        return redirect(url_for(views.task.task_detail, group_codename=group_codename, task_id=task_id))

@app.route('/group/<group_codename>/tasks/<int:task_id>/approve', methods=['GET','POST'])
def task_approve(group_codename, task_id):
    '''
    Displays the form required to approve a Task, calls the approve_task controller function once the
    Member actually submits the form to try and approve.  Sanity checks to make sure the Member trying
    to approve the Task is actually contained in approving_members.

    :param group_codename:
    :param task_id:
    :return:
    '''

    # First off, grab our infonav, group, task, and current member.
    (infonav, this_group, this_task) = views.get_context(group_codename=group_codename, task_id=task_id)
    current_member = views.get_current_member(group_codename=group_codename, current_user=current_user)

    # Sanity check: is this even an approving Member?
    if this_task.is_approving(current_member):

        # Okay, they're supposed to be here.  First, build up the form and our content object.
        form = forms.TaskApproveForm()
        content = {'task_name':this_task.name,
                   'deliverable':this_task.deliverable,
                   'deadline':this_task.deadline
        }

        # If they haven't submitted anything, that's it -- just show 'em the page!
        if not form.validate_on_submit():
            return render_template('templates/pages/tasks/approve.html', form=form, content=content, infonav=infonav)

        # Unless they have, in which case call the controller function, flash some messages, and redirect.
        else:
            try:
                controllers.task.approve_task(request, task_id, current_member.member_id)
                flash("Way to go, you just finished approving the Task called " + this_task.name + "!", "success")
                return redirect(url_for(views.task.task_list, group_codename=group_codename))
            except Exception as e:
                flash("Oh shoot, the approval failed for some reason.  Here's the deal: " + str(e), "error")
                return redirect(url_for(views.task.task_approve, group_codename=group_codename, task_id=task_id))

    else:
        # I'M NOT CRAZY.  This Member can't be here, punt them out.
        flash("Sorry, you can't approve that Task -- you're not an approving Member!", "error")
        return redirect(url_for(views.task.task_detail, group_codename=group_codename, task_id=task_id))