__author__ = 'John'

from flask import Flask, request, session, g, redirect, url_for,\
     abort, render_template, flash, make_response
from flask.ext.sqlalchemy import SQLAlchemy,Pagination
from groupbot.models import db_session, User

#----------------------------------------------------------------------------#
# Atomic Events for USERS.
#----------------------------------------------------------------------------#
def create_user(request):
    '''
    INPUT
    User Form with the mandatory arguments username, password, and email.
    Optional arguments real/display name, phone number, and 160 character
    bio.

    REQUIREMENT
    Username and email must be unique.

    OUTPUT
    Creates a User row in the database with all of the provided information
    associated with it.
    '''

    # Checks the optional fields with a ternary operator, uses the mandatory fields directly.
    print "request.form: ",request.form
    print "request.form['phone']: ",request.form['phone']
    phone = request.form['phone'] if request.form['phone'] != '' else None
    bio = request.form.bio.data if request.form['bio'] != '' else None
    photo = request.form.photo.data if request.form['photo'] != '' else None
    newUser = User(codename=request.form['codename'], password=request.form['password'],
                   first_name=request.form['first_name'], last_name=request.form['last_name'],
                   email=request.form['email'], phone=phone, bio=bio, photo=photo)
    db_session.add(newUser)
    db_session.commit()
    return newUser

def delete_user(user_id):
    '''
    INPUT
    User_ID of the account to be deleted.

    OUTPUT
    Removes the user's row from the database, purging all of their memberships.
    '''
    user = User.query.get(int(user_id))
    db_session.delete(user)
    db_session.commit()
    return True

def edit_user(user_id, request):
    '''
    INPUT
    A PasswordChangeForm, EmailChangeForm, or UserInfoChangeForm,
    along with the user's ID from the request.

    OUTPUT
    Modifies the user's row in the database as specified by whichever form
    was submitted
    '''
    user = User.query.get(int(user_id))
    if request.form['username']:
        username = request.form['username']
        user.username = username
    if request.form['password']:
        password = request.form['password']
        user.password = password
    if request.form['name']:
        name = request.form['name']
        user.name = name
    if request.form['email']:
        email = request.form['email']
        user.email = email
    if request.form['phone']:
        phone = request.form['phone']
        user.phone = int(phone)
    if request.form['bio']:
        bio = request.form['bio']
        user.bio = bio
    if request.form['photo']:
        photo = request.form['photo']
        user.photo = photo
    db_session.add(user)
    db_session.commit()
    return True