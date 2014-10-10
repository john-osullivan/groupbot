__author__ = 'John'

from flask import Flask, request, session, g, redirect, url_for,\
     abort, render_template, flash, make_response
import groupbot as gbot
from groupbot import app
from flask.ext.login import login_required, current_user
from groupbot.models import db_session, User, Group, Member, \
                                member_roles, Role, member_tasks, Task, \
                                Event
import groupbot.forms as forms

@app.route('/user/create', methods=['GET', 'POST'])
def user_create():
    form = forms.UserCreateForm(request.form)
    print("was form submitted? :",form.is_submitted())
    print("did form validate on submit? :",form.validate_on_submit())
    if form.validate_on_submit():
        try:
            gbot.controllers.user.create_user(request)
            flash("You just created an account called {0}!  Glad to have you, thanks for joining.".format(form.codename))
            return redirect(url_for(gbot.views.login()))
        except Exception as e:
            flash("Dang, that didn't work because: " + str(e))
            return redirect(url_for(user_create()))
    else:
        print form

    return render_template('pages/users/create.html', form=form)

@app.route('/user/<user_codename>/detail')
def user_detail(user_codename):
    user = User.query.filter_by(codename=user_codename).first()
    infonav = gbot.views.build_infonav('user')
    content = {
        'realname':current_user.first_name + " " + user.last_name,
        'email':user.email,
        'bio':user.bio,
        'photo_url':user.photo
    }
    return render_template('pages/users/detail.html', content=content, infonav=infonav)

@app.route('/user/<user_codename>/edit', methods=['GET', 'POST'])
def user_edit(user_codename):

    # First, make sure the user is editing their own profile.
    if user_codename == current_user.codename:

        # Populate the form with the user's values and then serve it.
        user = User.query.filter_by(codename=user_codename).first()
        form = forms.UserEditForm(request.form)
        form.code_name.data = user.code_name
        form.email.data = user.email
        form.name.first_name.data = user.first_name
        form.name.last_name.data = user.last_name
        form.phone.data = user.phone
        form.photo.data = user.photo
        form.bio.data = user.bio

        # If the forms been submitted, perform the edit and redirect with a successful flash.
        if form.validate_on_submit():
            try:
                gbot.controllers.user.edit_user(current_user.user_id, request)
                flash("You successfully edited your user page!", "success")
                return redirect(url_for(gbot.views.group.group_list()))

            # Unless something goes wrong!  Then let them know what just done did happen.
            except Exception as e:
                flash("Whoa, that didn't work!  Check it out: " + str(e))
                return redirect(url_for(user_edit(user_codename)))

        # Assuming they haven't submitted the form yet, show 'em the form.
        return render_template('pages/users/edit.html', form=form)

    # Otherwise, deny 'em access.
    else:
        flash("You can't edit that page, it's not yours!")
        return redirect(url_for(gbot.views.group.group_list))

@app.route('/user/<user_codename>/delete', methods=['GET', 'POST'])
def user_delete(user_codename):

    # First, make sure the User is trying to delete their own profile.  No fucking other people over.
    if user_codename == current_user.codename:

        # Populate the page in case they look at it.
        form = forms.DeleteForm(request.form)
        content = {'codename':current_user.codename}

        if form.validate_on_submit():

            # Then, if they go through with it, delete the account.
            if form.delete:
                flash("We're sad to see you go, {0} :(".format(current_user.code_name))
                gbot.controllers.user.delete_user(current_user.user_id)
                return redirect(url_for(gbot.views.home()))

            # Make sure to say thank you if they don't, though!
            else:
                flash("Glad you chose to stick around, " + str(current_user.codename))
                return redirect(url_for(gbot.views.group.group_list()))


        # Of course, if they haven't actually submitted it yet, just show 'em the darn page!
        return render_template('pages/users/delete.html', content=content, form=form)

    # If you're trying to see the delete page for someone else's profile, get outta here
    else:
        flash("You can't delete this account, it ain't even yours to begin with!", "error")
        return redirect(url_for(gbot.views.group.group_list()))
