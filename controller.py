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
    '''
    '''

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
    # db_session.commit()
    return True

#----------------------------------------------------------------------------#
# Atomic Events for GROUPS.
#----------------------------------------------------------------------------#

@app.route('/group/create')
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
    # flash("You just created {0}!".format(str(request.form['display_name'])))
    return True

@app.route('/group/<group_code_name>/delete')
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
    # flash('You\'ve deleted the group "{0} ({1})."'.format(human_name, code_name))
    return True

@app.route('/group/<group_code_name>/edit')
def edit_group(group_code_name):
    '''
    INPUT
    A filled-out GroupForm which validates.  Essentially, the edit uses the same
    view as the create.  It allows you to update the description, by-line, and
    display name. 
    '''
    # Grab object we're changing
    group = Group.query.filter_by(code_name = group_code_name)
    
    # Grab new values from form
    new_name = request.form['human-name']
    new_byline = request.form['by-line']
    new_desc = request.form['description']
    
    # Modify the object
    group.human_name = new_name
    group.byline = new_byline
    group.description = new_desc

    # Commit our changes to the session
    db_session.commit()
    return True

@app.route('/bond/create')
def create_bond():
    '''
    INPUT
    Requires the two group's IDs to be in the request, formatted as:
    request['groups'] = [group1_id, group2_id]

    OUTPUT
    Creates the object in the database.  The Bond initializier handles the creation of
    necessary associations in the foreign key.
    '''
    
    # Get the IDs encoded in the request.
    (group1_id, group2_id) = request.POST['groups']

    # Give them to the Bond initializer, then add and save the new Bond.
    new_bond = Bond(group1_id, group2_id)
    db_session.add(new_bond)
    db_session.commit()
    return True

@app.route('/bond/<int:bond_id>/delete')
def delete_bond(bond_id):
    '''
    INPUT
    Takes the IDs of the Bond being deleted from the URL.  Needs to find the group_ids in 
    the Bond encoded in the request (same syntax as create), for validation's sake.  

    (Once there's a Permission's system built in, it should also take the Member's ID
    to make sure they have Permission to make that action.)

    OUTPUT
    Deletes the object
    '''
    (group1_id, group2_id) = request.POST['groups']
    group1 = Group.query.get(group1_id)
    group2 = Group.query.get(group2_id)
    dead_bond = Bond.query.get(bond_id)
    bond_groups = dead_bond.groups
    if (group1 in bond_groups) and (group2 in bond_groups):
        db_session.delete(dead_bond)
        db_session.commit()
        return True
    else:
        raise Exception("The group's specified weren't part of the Bond to be deleted!")

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
    return True

@app.route('/member/<int:member_id>/edit')
def edit_member(member_id):
    '''
    INPUT
    A Member ID whose profile is being edited, a validated MemberForm to update
    their information.

    RESULT
    Updates the Member's information, returns True if successful and throws an
    Exception if it wasn't.
    '''
    member = Member.query.get(member_id)
    new_name = request.form['preferred_name']
    member.preferred_name = new_name
    return True

@app.route('/member/<int:member_id>/remove')
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
    return True

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
    return True

@app.route('/role/<int:role_id>/delete')
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
    return True

# Gives a Role to a specific Member
@app.route('/role/<int:role_id>/assign')
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
    return True

@app.route('/role/<int:role_id>/remove')
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
    return True

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

    # Grab the information of the creator group & member
    group_id = request.POST['group_id']
    giver_member_id = request.POST['member_id']

    # Grab the mandatory information associated with the task
    name = request.form['name']
    doer_member_id = request.POST['doing_member']

    # Grab the optional information associated with the task
    if request.form['parent_id'] != None: parent_id = request.form['parent_id'] else: parent_id = None
    if request.form['deadline'] != None: deadline = request.form['deadline'] else: deadline = None
    if request.form['description'] != None: description = request.form['description'] else: description = None
    if request.form['comments'] != None: comments = request.form['comments'] else: comments = None
    if request.form['points'] != None: points = int(request.form['points']) else: points = None

    # Create the task and set its optional parameters
    new_task = Task(name, doer_member_id, giver_member_id, group_id)
    new_task.deadline = deadline
    new_task.description = description
    new_task.comments = comments
    new_task.points = points
    new_task.parent = Task.query.get(parent_id)

    # Add and save our work.
    db_session.add(new_task)
    db_session.commit()
    return True

@app.route('/task/<int:task_id>/edit')
def edit_task(task_id):
    '''
    INPUT
    Uses the task_id to get the Task object, uses any updated parameters from the form
    to change its attributes.  Assumes, as always, that the group_id and member_id are
    coming through the request.

    RESULT
    The Task is updated in the database -- what did you think was going to happen?  True
    if success, Exception if not.
    '''
    # Grab the task we're talking about
    task = Task.query.get(task_id)
    
    # Grab any new values from the form, choose the old ones if the form field wasn't updated.
    if request.form['name'] != task.name: new_name = request.form['name'] else: new_name = task.name
    if request.form['description'] != task.description: new_desc = request.form['description'] else: new_desc = task.description
    if request.form['doing_member'] != task.doing_member: new_doing_member = request.form['doing_member'] else: new_doing_member = task.doing_member
    if request.form['deadline'] != task.deadline: new_deadline = request.form['deadline'] else: new_deadline = task.deadline
    if int(request.form['points']) != task.points: new_points = int(request.form['points']) else: new_points = task.points
    if request.form['comments'] != task.comments: new_comments = request.form['comments'] else: new_comments = task.comments

    # Modify the Task to fit our new values.
    task.name = new_name
    task.description = new_desc
    task.doing_member = new_doing_member
    task.deadline = new_deadline
    task.points = new_points
    task.comments = new_comments

    # No need to add, since the object already exists in the database!
    db_session.commit()
    return True

@app.route('/task/<task_id>/delete')
def delete_task(int:task_id):
    '''
    INPUT
    Triggered via a close button element, handed the task_id implicitly from the
    page request.  Assumes there will be a member_id and group_id in the request.

    REQUIREMENT
    Can only be used before a task has been delivered.

    OUTPUT
    Removes a Task entry from the database, erasing it from the Tasks of each
    Member.
    '''
    # Grab the Group, Member, and Task we need.
    group = Group.query.get(request.POST['group_id'])
    member = Member.query.get(request.POST['member_id'])
    task = Task.query.get(task_id)

    # Make sure the Task and Member are both part of the Group.
    if ((task.group_id == group.id) and (task.giving_id == member.id)):
        # Then delete the object from the database and save the change.
        db_session.delete(task)
        db_session.commit()
        return True
    else:
        raise Exception("Either the Task wasn't part of the given group, or you weren't!")

# Used to deliver tasks.
@app.route('/task/<int:task_id>/deliver')
def deliver_task(task_id):
    '''
    INPUT
    Triggered via a delivery mechanism.  Only requires the task_id and a reference
    to the deliverable which completed it.  If an already delivered task is delivered
    again, the new deliverable overwrites the old one.  Assumes that request.POST['deliverable']
    has something in it -- text, image, file, whatever.  For now, it's stored as binary data.

    OUTPUT
    Changes the delivered Boolean of the specified Task to True, puts whatever was stored at
    that part of the request into the Task.deliverable attribute.
    '''
    group = Group.query.get(request.POST['group_id'])
    delivering_member = Group.query.get(request.POST['member_id'])
    task = Task.query.get(task_id)
    deliverable = request.POST['deliverable']
    if (task.doing_member == delivering_member):
        task.delivered = True
        task.deliverable = deliverable
        db_session.commit()
        return True
    else:
        raise Exception("The person turning this in isn't the one who was supposed to!")

@app.route('/task/<int:task_id>/approve')
def approve_task(task_id):
    '''
    INPUT
    Requires the task_id and the ID of the request submitter.  Checks to make 
    sure the person approving the task is one of the people who assigned it.

    OUTPUT
    Changes the approved boolean of the task to True.  If Points are enabled,
    the points are then awarded to the doer of the task.
    '''
    group = Group.query.get(request.POST['group_id'])
    approving_member = Group.query.get(request.POST['member_id'])
    task = Task.query.get(task_id)
    if (task.giving_id == approving_member.member_id):
        task.approved = True
        task.doing_member.points += task.points
        db_session.commit()
        return True
    else:
        raise Exception("The person submitting this approval isn't the one who was supposed to!")


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
    # Grab the standard Group and Member so we know who and where the request is coming from.
    group_id = request.POST['group_id']
    member_id = request.POST['member_id']

    # Grab the mandatory parameters out of the form
    name = request.form['name']
    host_id = request.form['host']
    start_time = request.form['start_time']
    location = request.form['location']

    # Grab the two optional parameters.
    if request.form['end_time'] != "": end_time = request.form['end_time'] else: end_time = None
    if request.form['description'] != "": description = request.form['description'] else: description = None

    # Make a new object, set its parameters which aren't handled by the init function.
    new_event = Event(name, group_id, start_time, end_time, host_id, description)
    db_session.add(new_event)
    db_session.commit()

@app.route('/event/<int:event_id>/delete')
def delete_event(event_id):
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

@app.route('/event/<int:event_id>/edit')
def edit_event(event_id):
    '''
    INPUT
    Member object in the request to check permissions.  Also an Event form in order to
    update the contents of this one.

    RESULT
    If all goes well, event is edited and returns True.  Otherwise, an Exception.
    '''
    # Grab the event as well as the standard Group and Member so we know who and where the 
    # request is coming from.
    group_id = request.POST['group_id']
    member_id = request.POST['member_id']
    event = Event.query.get(event_id)

    # Check if each parameter was updated, grab the valid version (updated or still in database)
    if request.POST['updated']:
        event.name = request.form['name']
        event.host_id = request.form['host_id']
        event.start_time = request.form['start_time']
        event.end_time = request.form['end_time']
        event.location = request.form['location']
        event.description = request.form['description']
        db_session.commit()

@app.route('/event/<int:event_id>/invite')
def invite_member(event_id):
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
    group_id = request.POST['group_id']
    inviting_member = Member.query.get(request.POST['member_id'])
    event = Event.query.get(event_id)
    
    # Check to make sure the inviting Member is a host.
    if inviting_member in event.host:

        # Grab the Member who was invited and add them to the invited relation.
        invited_member = Member.query.get(request.form['member'])       
        event.invited.append(invited_member)
        db_session.commit()
    else:
        raise Exception("That Member can't invite someone, they're not a host!")

@app.route('/event/<int:event_id>/rsvp')
def rsvp(event_id):
    '''
    INPUT
    Member object in the request to make sure they were invited to begin with. Other
    than that, the event_id is enough to work things out.    

    RESULT
    The Member is added to the Event's .rsvp_yes attribute.  The function returns
    True to confirm successful operation, Exception if it fails.
    '''
    # Grab the standard Group and Member so we know who and where the request is coming from.
    group_id = request.POST['group_id']
    rsvp_member = Member.query.get(request.POST['member_id'])
    event = Event.query.get(event_id)
    if rsvp_member in event.invited:
        attending = request.form['attending']
        if attending: # Note, this works specifically because the form's value for Yes is True.
            event.rsvp_yes.append(rsvp_member)
        else:
            event.rsvp_no.append(rsvp_member)
        db_session.commit()
    else:
        return Exception("That member wasn't even invited to this event!")


@app.route('/event/<int:event_id>/attend')
def attend(event_id):
    '''
    INPUT
    Need a Member object in the request, representing the Member who attended.  This may not
    be the Member who calls the function, so it's important to make sure we're putting the
    right Member's information in.  Other than that, we're good with event_id.

    RESULT
    Member is added to the Event's .attended_yes attribute.  Same success:True, 
    failure:Exception behavior as elsewhere.
    '''
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

@app.route('/event/<int:event_id>/missEvent')
def miss_event(event_id):
    '''
    INPUT
    Need a Member object in the request, representing the Member who didn't attend.  
    Other than that, we're good with event_id.

    RESULT
    Member is added to the Event's .attended_no attribute.  Same success:True,
    failure:Exception behavior as seen elsewhere.
    '''


#----------------------------------------------------------------------------#
# Infopages.
#----------------------------------------------------------------------------#
@app.route('/info/create')
def create_infopage():
    '''
    NOTE
    This function is meant to be a barebones creator of an InfoPage.  Given their 

    INPUT
    Member object in the request, in order to check that Permissions are valid.
    Additionally a validated InfoPageForm.

    RESULT
    Infopage is created, the function returns True if everything goes well.  If
    something breaks, it'll throw an Exception.
    '''

@app.route('/info/<int:info_id>/delete')
def delete_infopage(info_id):
    '''
    INPUT
    Member object in the request, in order to check that Permissions are valid.

    RESULT
    Infopage is deleted, it returns True if all goes well -- otherwise it
    throws an Exception.
    '''

@app.route('/info/<int:info_id>/edit')
def edit_infopage(info_id):
    '''
    INPUT
    A validated InfoPageForm which has the sanitized HTML string we need to save.
    Member object in the request, in order to check that Permissions are valid.

    RESULT
    Infopage has its content updated, it returns True if all goes well -- otherwise
    it throws an Exception.
    '''

#----------------------------------------------------------------------------#
# Representatives.
#----------------------------------------------------------------------------#


#----------------------------------------------------------------------------#
# Committee.
#----------------------------------------------------------------------------#