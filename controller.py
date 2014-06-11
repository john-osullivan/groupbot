from flask import Flask, request, session, g, redirect, url_for,\
     abort, render_template, flash, make_response
from flask.ext.sqlalchemy import SQLAlchemy,Pagination
from app import app
from models import db_session, User, GroupPartnership, Group, Member, \
                                member_roles, Role, member_tasks, Task


##############################################
#----------------------------------------------------------------------------#
# Data Manipulators.
#----------------------------------------------------------------------------#
##############################################

#----------------------------------------------------------------------------#
# Atomic Events for USERS.
#----------------------------------------------------------------------------#
@app.route('/user/create', methods=['POST'])
def create_user():
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
    if request.form['name']: display_name = request.form['name'] else: display_name = None
    if request.form['phone']: phone = request.form['phone'] else: phone = None
    if request.form['bio']: bio = request.form['bio'] else: bio = None
    newUser = User(username = request.form['username'], password = request.form['password'],\
                                name=display_name, email=request.form['email'], phone=phone,\
                                bio=bio)
    db_session.add(newUser)
    db_session.commit()
    flash("You're a user of Groupify now, {0}!".format(str(request.form['username'])))
    return render_template('user_dash.html') 

@app.route('/user/<username>'):
def view_user(username):

@app.route('/user/<username>/delete')
def delete_user(username):
    '''
    INPUT
    User_ID of the account to be deleted.

    OUTPUT
    Removes the user's row from the database, purging all of their memberships.
    '''
    user_id = request.POST['user_id']
    user = User.query.get(int(user_id))
    username = str(user.username)
    db_session.delete(user)
    db_session.commit()
    flash("We're sad to see you go, {0} :(".format(username))
    return render_template('home.html')

@app.route('/user/<username>/edit')
def edit_user(username):
    '''
    INPUT
    A PasswordChangeForm, EmailChangeForm, or UserInfoChangeForm,
    along with the user's ID from the request.

    OUTPUT
    Modifies the user's row in the database as specified by whichever form
    was submitted
    '''
    user_id = request.POST['user_id']
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
    return render_template('user_dash.html')

#----------------------------------------------------------------------------#
# Atomic Events for GROUPS.
#----------------------------------------------------------------------------#

@app.route('/createGroup')
def create_group():
    '''
    INPUT
    Takes a GroupForm with the mandatory arguments of DIsplay Name
    and Code Name, optional argumets of By-Line and Description.

    OUTPUT
    Creates a new Group with the specified information.  The User who
    created the Group is both its first Member and the administrator (which
    is the default first role in every group).
    '''
    if request.form['byline']: byline = request.form['byline'] else: byline = None
    if request.form['description']: description = request.form['description'] else: description = None
    new_group = Group(human_name = request.form['display_name'], \
                                    code_name = request.form['code_name'], \
                                    byline = byline, description = description)
    db_session.add(new_group)
    db_session.commit()
    flash("You just created {0}!".format(str(request.form['display_name'])))
    return render_template('group_home.html', group=new_group)

@app.route('/group/<group_code_name>/deleteGroup')
def delete_group(group_code_name):
    '''
    INPUT
    Takes the ID of the group and the User_ID of the person who submitted
    the request for deletion.

    OUTPUT
    Deletes the Group from the database, including all of its Members, Roles,
    and Tasks.  If the User_ID does not match up with that of
    the administrator, the request does not succeed.
    '''
    group_id = request.POST['group_id']
    group = Group.query.get(group_id)
    code_name = str(group.code_name)
    human_name = str(group.human_name)
    db_session.delete(group)
    db_session.commit()
    flash('You\'ve deleted the group "{0} ({1})."'.format(human_name, code_name))
    return render_template('user_dash.html')

@app.route('/group/joinPartnership/<group_code_name>/<other_group_code_name>')
def join_partnership(group_code_name, other_group_code_name):
    '''
    INPUT
    Takes the IDs of the partnership and the new partner.

    OUTPUT
    Add the partner to the Partnership Group's Partners relation.  Conversely, 
    it also adds the partnership to the partner's Partnerships relation.  If the
    groups are already partnered, an Exception is thrown.  If the groups are 
    already part of a parent or child relationship with each other, an Exception
    is thrown.
    '''
    return None

@app.route('/group/leavePartnership/<group_code_name>/<other_group_code_name>')
def leave_partnership(group_code_name, other_group_code_name):
    '''
    INPUT
    Takes the IDs of the partnership and partner.

    OUTPUT
    Removes the Partner from the Partnership Group's Partners relation.  This
    has the equivalent effect of removing the Partnership Group from the 
    Partner Group's Partnership relation.  If the groups aren't partnered, 
    it throws an Exception saying so.
    '''
    return None


# THIS IS CONTROLLER FUNCTIONALITY FOR HIERARCHICAL, PARENT:CHILD GROUPS.
# Since we're not using that route right now, it's commented out.
#
# @app.route('/createSubgrouping')
# def create_subgrouping():
#     '''
#     INPUT
#     Takes the IDs of the parent and child groups.

#     OUTPUT
#     Sets the child's parent_id attribute to the ID of the parent group.  Adds the
#     child's ID to the parent's children ForeignKey relation.
#     '''
#     return None

# @app.route('/deleteSubgrouping')
# def delete_subgrouping():
#     '''
#     INPUT
#     Takes the IDs of the parent and child groups.

#     OUTPUT
#     Sets the child's parent_id attribute to null, simultaneously removing it
#     from the parent group's children ForeignKey relation.
#     '''
#     return None

#----------------------------------------------------------------------------#
# Atomic Events for MEMBERS.
#----------------------------------------------------------------------------#

@app.route('/member/add')
def add_member(group_code_name):
    '''
    INPUT
    A group ID, a user ID, and a Member Form which only has one (optional)
    argument of a Preferred Name.  Letting people decide who they are based
    on where they are is generally a nice thing.

    OUTPUT
    Create a new Member row associated with the User and Group, possibly
    holding a value for Preferred Name.  The Role and Task relations are 
    empty by default. 
    '''
    group_id = request.POST['group_id']
    group = Group.query.get(group_id)
    if request.form['preferred_name']: pref_name = request.form['preferred_name'] else: pref_name = None
    new_member = Member(group_id=group_id, preferred_name=pref_name)
    return render_template('group_home.html', group = group)

@app.route('/member/<member_id>/remove')
def remove_member(member_id):
    '''
    INPUT
    A  Member ID for the member to be removed.

    OUTPUT
    Removes the specified Member's row from the database, removing them 
    from all Roles they were assigned to.  If a Task was only assigned to them,
    it is removed as well.
    '''
    member_id = request.POST['member_id']
    group_id = request.POST['group_id']
    member = Member.query.get(member_id)
    group = Group.query.get(group_id)
    db_session.delete(member)
    db_session.commit()
    return render_template('group_home.html', group = group)

#----------------------------------------------------------------------------#
# Atomic Events for ROLES.
#----------------------------------------------------------------------------#

@app.route('/role/create')
def create_role():
    '''
    INPUT
    Takes a Group_ID, optional Member_ID, and RoleForm -- which has the 
    mandatory argument of a role name and an optional argument of role
    description.

    OUTPUT
    Creates a Role within the specified Group that has the specified description.
    If a Member_ID is supplied, that Member automatically becomes the first 
    person to hold the Role.
    '''
    group_id = int(request.POST['group_id'])
    role_name = request.form['name']
    if request.form['description']: description = request.form['description'] else: description = None
    if request.form['member']: member = int(request.form['member']) else: member = None
    new_role = Role(group_id = group_id, name = role_name, \
                                description = description, member_id = member)
    db_session.add(new_role)
    db_session.commit()
    return render('group_home.html', group = group)

@app.route('/role/<role_id>/delete')
def delete_role(role_id):
    '''
    INPUT
    Takes a Role_ID to be deleted.

    OUTPUT
    Removes the Role's row from the database.  It is therefore no longer associated
    with any members.  If there are any Tasks only approved by that Role, then the
    approval responsibilities move to the people who were last holding said Role.
    '''
    group_id = int(request.POST['group_id'])
    group = Group.query.get(group_id)
    role_id = int(request.POST['role_id'])
    role = Role.query.get(role_id)
    if role.group_id == group_id:
        db_session.delete(role)
        db_session.commit()
    return render('group_home.html', group=group)

# Gives a Role to a specific Member
@app.route('/role/<role_id>/assign')
def assign_role(role_id):
    '''
    INPUT
    Takes a Group_ID, Role_ID, and Member_ID.

    OUTPUT
    Adds the Member to the Member_ID propety of the specified Role in the
    specified Group.  If the Member is already assigned to the Role, throws an
    Exception saying that Role was already assigned to that Member.
    '''
    # Get IDs from the request
    group_id = int(request.POST['group_id'])
    role_id = int(request.POST['role_id'])
    member_id = int(request.POST['member_id'])

    # Grab the actual Role & Member objects using the provided IDs.
    group = Group.query.get(group_id)
    role = Role.query.get(role_id)
    member = Member.query.get(member_id)

    # Next, run a sanity check to make sure that Role is part of the Member's Group
    if role not in group.roles:
        raise Exception("This Role isn't a part of that Group, it can't go to that Member!")

    # Finally, add the Member to the Role's Role.member_id property and commit.
    role.member_id.append(member)
    db_session.add(role)
    db_session.commit()
    return render_template('group_home.html')

@app.route('/role/<role_id>/remove')
def remove_role(role_id):
    '''
    INPUT
    Takes a Group_ID, Role_ID, and Member_ID.

    OUTPUT
    Removes the specified Member from the specified Role's Member_ID
    relation.  If the Member was not actually in that relation, throws an 
    Exception saying the specified Member did not have that Role.
    '''
    group_id = int(request.POST['group_id'])
    role_id = int(request.POST['role_id'])

    group = Group.query.get(group_id)
    role = Role.query.get(role_id)

    if role not in group.roles:
        raise Exception("This Role isn't a part of that Group to begin with!")
    else:
        db_session.delete(role)
        db_session.commit()
        flash("The '{0}' was deleted from the '{1}' group.".format(role.name, group.human_name))
    return render_template('group_home.html', group=group)

#----------------------------------------------------------------------------#
# Atomic Events for TASKS.
#----------------------------------------------------------------------------#

@app.route('/task/create')
def create_task():
    '''
    INPUT
    Takes in a submission of the create task form, gathering the Title, 
    Description, Deadline, Assignee, and optional Points arguments.  Also takes
    the Group ID and Assigner ID implicitly from the page request.

    OUTPUT
    Creates a new Task entry in the database associated with all relevant
    parties, adding it to the Tasks for each Member assigned.
    '''
    return None

@app.route('/task/<task_id>/edit')
def edit_task(task_id):
    '''
    INPUT

    RESULT
    
    '''

@app.route('/task/<task_id>/delete')
def delete_task(task_id):
    '''
    INPUT
    Triggered via a close button element, handed the task_id implicitly from the
    page request.

    REQUIREMENT
    Can only be used before a task has been delivered.

    OUTPUT
    Removes a Task entry from the database, erasing it from the Tasks of each
    Member.
    '''
    return None

# Used to deliver tasks.
@app.route('/task/<task_id>/deliver')
def deliver_task(task_id):
    '''
    INPUT
    Triggered via a delivery mechanism.  Only requires the task_id and a reference
    to the deliverable which completed it.  If an already delivered task is delivered
    again, the new deliverable overwrites the old one.

    OUTPUT
    Changes the delivered Boolean of the specified Task to True.
    '''
    return None

@app.route('/task/<task_id>/approve')
def approve_task(task_id):
    '''
    INPUT
    Requires the task_id and the ID of the request submitter.  Checks to make 
    sure the person approving the task is one of the people who assigned it.

    OUTPUT
    Changes the approved boolean of the task to True.  If Points are enabled,
    the points are then awarded to the doer of the task.
    '''
    return None


#----------------------------------------------------------------------------#
# Atomic Events for EVENTS
#----------------------------------------------------------------------------#

@app.route('/event/create')
def create_event():
    '''
    INPUT
    Member object in the request to make sure Permissions are valid.  Also a filled
    out EventCreate form.

    REQUIRES
    Member object in the request.

    RESULT
    If all goes well, event is created and returns True.  Otherwise, an Exception.
    '''

@app.route('/event/<event_id>/delete')
def delete_event(group_code_name, event_id):
    '''
    INPUT

    REQUIRES
    Member object in the request.

    RESULT
    If all goes well, event is deleted and returns True.  Otherwise, an Exception.
    '''

@app.route('/event/<event_id/edit')
def edit_event(group_code_name, event_id):
    '''
    INPUT
    Member object in the request to check permissions.  Also a fresh EventCreate form
    in order to update the contents of this one.

    RESULT
    If all goes well, event is edited and returns True.  Otherwise, an Exception.
    '''

@app.route('/event/<event_id>/rsvpEventYes')
def rsvp_event_yes(group_code_name, event_id):
    '''
    INPUT

    REQUIRES
    Member object in the request.

    RESULT
    
    '''

@app.route('/event/<event_id>/rsvpEventNo')
def rsvp_event_no(group_code_name, event_id):
    '''
    INPUT

    REQUIRES
    Member object in the request.

    RESULT
    
    '''

@app.route('/event/<event_id>/attendEvent')
def attend_event(group_code_name, event_id):
    '''
    INPUT
    REQUIRES
    Member object in the request.

    RESULT
    
    '''

@app.route('/event/<event_id>/missEvent')
def miss_event(group_code_name, event_id):
    '''
    INPUT

    REQUIRES
    Member object in the request.

    RESULT
    
    '''


#----------------------------------------------------------------------------#
# Infopages.
#----------------------------------------------------------------------------#
@app.route('/info/create')
def create_infopage():
    '''
    INPUT

    REQUIRES
    Member object in the request, in order to check that Permissions are valid.

    RESULT

    '''

@app.route('/info/<info_id>/delete')
def delete_infopage(info_id):
    '''
    INPUT
    Member object in the request, in order to check that Permissions are valid.

    RESULT
    Infopage is deleted, it returns True if all goes well -- otherwise it
    throws an Exception.
    '''

@app.route('/info/<info_id>/edit')
def edit_infopage(info_id):
    '''
    INPUT
    A string of sanitized HTML (via some text editor JS library) which overrides all
    the relevant fields in an Infopage.  Member object in the request, in order to 
    check that Permissions are valid.

    RESULT
    Infopage has its content updated, it returns True if all goes well -- otherwise
    it throws an Exception.
    '''
