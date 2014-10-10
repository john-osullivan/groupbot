__author__ = 'John'
import groupbot.helper
from flask.ext.login import current_user, login_user

from flask import request, redirect, url_for, render_template, flash
from groupbot import app, forms
import groupbot.models as m
import user, group, role, task, event, member



__all__ = ['user', 'group', 'role', 'task', 'event', 'member']


# Context Processor: Puts in basic keywords to views so that anything works
@app.context_processor
def inject_groupbot():
    return dict(views=groupbot.views,
                list_routes = list_routes)

###############################################
#---------------------------------------------#
# Controllers.
#---------------------------------------------#
###############################################
def list_routes():
    import urllib
    output = []
    for rule in app.url_map.iter_rules():

        print rule
        print "Endoint: " + str(rule.endpoint)
        print ""
        # options = {}
        # for arg in rule.arguments:
        #     options[arg] = "[{0}]".format(arg)
        #
        # methods = ','.join(rule.methods)
        # url = url_for(rule.endpoint, **options)
        # line = urllib.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, url))
        # output.append(line)

    for line in sorted(output):
        print line


@app.route('/')
def index():
    print "Hit the index function"
    if current_user.is_anonymous():
        # This person isn't logged in, show them the landing page
        return render_template('pages/landing.html')
    else:
        # Hey, this is just a good user trying to get at the site!  Show 'em
        # the group list.
        return redirect(url_for(groupbot.views.group.group_list))

@app.route('/about')
def about():
    print "Well, it's TRYING to show me the about page..."
    return render_template('pages/about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm(request.form)
    if form.validate_on_submit():
        print form.codename
        user = m.User.query.filter_by(codename=form.codename._value()).first()
        if user is not None:
            login_user(user)
        else:
            flash("We couldn't find an account with that name, sorry!")
            return redirect(url_for('login'))
        return redirect(url_for('group_list'))
    else:
        print "form.data: ",form.data
        print "form.validate(): ",form.validate()
    return render_template('forms/login.html', form = form)

@app.route('/forgot')
def forgot():
    form = forms.ForgotForm(request.form)
    return render_template('forms/forgot.html', form = form)

###############################################
#---------------------------------------------#
# Standard Infopage view functions, essentially View helpers.
#---------------------------------------------#
###############################################
def build_infonav(level, current_group=None, member=None):
    '''
    This function produces the information required to construct the (now simplified) navbar.  The level
    parameter determines whether we should be passing in the list of groups (for the top-level dashboard view)
    or instead be passing in the information required to show one group (for the group detail view).

    :param level:
    :return infonav:
    '''

    # First, make our infonav object
    infonav = {}

    # If we're at the user level, we just need the sidebar to list each of the user's groups
    if level == 'user':
        infonav['parent'] = {'name': current_user.code_name,
                             'view': groupbot.views.group.group_list}
        user_groups = app.helper.get_groups_from_user(current_user)
        infonav['pages'] = []
        for each_group in user_groups:
            infonav['pages'].append({
                'name':each_group.code_name,
                'view':groupbot.views.group.group_detail
            })

    # At the group level, however, we want to list all the vital information from each group.
    # Namely, we need links to Tasks, Events, Roles, and Members.  Tasks and Events have the five
    # upcoming objects as children along with a link to the actual List page, Role and Member
    # have no children -- just a link to the list page.
    elif level == 'group':
        # First off, make sure the group is defined -- otherwise we're borked!
        if current_group == None:
            raise Exception("No Group supplied to create infonav!")
        else:
            # Assuming it's defined, get the parent listing set up
            infonav['parent'] = {'name': current_group.code_name,
                                 'view': groupbot.views.group.group_detail,
                                 'args': {'group_id': current_group.group_id}}

            # Now the fun part.  First, add the links for Members and Roles
            infonav['pages'] = []
            infonav['pages'].append({
                'name': 'Members',
                'view': member.member_list
            })
            infonav['pages'].append({
                'name': 'Roles',
                'view': groupbot.views.role.role_list
            })

            # Now, make the objects required to populate Tasks and its children
            task_view = {'name':'Tasks',
                         'view':groupbot.views.task.task_list}
            upcoming_tasks = m.Task.query.filter_by(group_id = current_group.id).order_by(m.Task.deadline).limit(5)
            task_view['children'] = []
            for each_task in upcoming_tasks:
                task_view['children'].append({'name':each_task.name,
                                              'view':groupbot.views.task.task_detail,
                                              'args':{'task_id':each_task.task_id}})
            infonav['pages'].append(task_view)

            # Same story, but now with the Group's Events
            event_view = {'name':'Events',
                          'view':groupbot.views.event.event_list}
            upcoming_events = m.Event.query.filter_by(group_id = current_group.id).order_by(m.Event.start_time).limit(5)
            for each_event in upcoming_events:
                event_view['children'].append({'name':each_event.name,
                                               'view':groupbot.views.event.event_detail,
                                               'args':{'event_id':each_event.event_id}})
            infonav['pages'].append(event_view)


    return infonav

def get_group_and_nav(group_codename):
    '''
    Given a group_codename (aka every page but User), this builds up the infonav and gets the
    Group object.  Talk about a helper method.
    '''
    this_group = m.Group.query.filter_by(codename=group_codename).first()
    infonav = build_infonav('group', current_group=this_group)
    return (this_group, infonav)

def get_context(user_codename=None, group_codename=None, member_codename=None, role_id=None, event_id=None, task_id=None, ):
    '''
    Now, this thing should be the be-all end-all to just get the relevant information.  It can
    accept any number of arguments within [group_codename, member_codename, role_id, task_id, event_id].
    It then returns the associated objects.  "Associated objects" also always includes the appropriate
    infonav object.  If there's a group_codename, it goes on the Group level.  If there isn't, it goes
    on the User level.  Either way, this ALWAYS returns an infonav.  Otherwise, the number of arguments
    it returns is based on the number of arguments you give it.  Namely, you're going to get a number of
    responses equal to the number of arguments, plus one more for that infonav.

    GIANT DESIGN CAVEAT:
    The way it's written, when this function is called with tuple unpacking, you have to write the tuple
    with the arguments in the same order as they're written in the method signature.  I'll work on
    coming up with something better, but for now this works.  It logically processes through the codenames
    and then the ids in order of functional importance... I guess.  That's what I thought when I was
    writing it.  The order is:

    (user_codename, group_codename, member_codename, role_id, event_id, task_id)
    '''

    # Okay, HERE'S THE PLAN.  We just check if each argument is non-None and then add that to the back
    # of a list of objects.  At the end of everything, cast it to a tuple and pass it back.

    returning_records = []

    if user_codename is not None:
        returning_records.append(build_infonav('user'))
        returning_records.append(m.User.query.filter_by(codename=user_codename).first())

    elif group_codename is not None:
        infonav = build_infonav('group', current_group=group_codename)
        this_group = m.Group.query.filter_by(codename=group_codename).first()
        returning_records.append(infonav)
        returning_records.append(this_group)

    # Sanity check -- after checking for a User or Group, the list should be TWO parts long.
    if len(returning_records) != 2:
        raise Exception("We should've made the infonav by now in get_context() but we haven't!")

    # Moving on, do the same shit for every other datatype -- in the right order, of course.
    # On second thought...  We should only get one of these at a time.  It should actually just
    # be an elif.  After all, look at the URl schema -- it's group/subthing, not group/subthing/subthing.
    if member_codename is not None:
        this_member = m.Member.query.filter_by(group_id=this_group.group_id, codename=member_codename).first()
        returning_records.append(this_member)

    elif role_id is not None:
        returning_records.append(m.Role.query.get(role_id))

    elif event_id is not None:
        returning_records.append(m.Event.query.get(event_id))

    elif task_id is not None:
        returning_records.append(m.Task.query.get(task_id))

    return tuple(returning_records)

# def build_infopage(infopage):
#     '''
#     This function goes through the effort of building up the convoluted, general-ass
#     object that constitutes each and every one of our pages.  Specifically, it:
#     1) Grabs the info specific to the active page
#     2) Grabs the info for each infoblock using its content_func attribute
#
#     :param infopage:
#     :return:
#     '''
#     infonav = build_infonav(infopage)
#     info = {}
#     info['name'] = infopage.name
#     info['description'] = infopage.description
#     thing = class_table[]
#
#     return render_template('pages/infopage.html', infonav=infonav, infopage=info)

def get_group_and_member(group_codename, member_codename):
    this_group = m.Group.query.filter_by(codename = group_codename)
    this_member = m.Member.query.filter_by(group_id = this_group.group_id, codename = member_codename)
    return (this_group, this_member)

def get_current_member(group_codename, current_user):
    current_group = m.Group.query.filter_by(codename=group_codename).first()
    return m.Member.query.filter_by(group_id=current_group.group_id, user_id=current_user.user_id).first()

def group_and_member_from_user_and_groupname(user_id, group_codename):
    this_group = m.Group.query.filter_by(codename=group_codename).first()
    this_member = m.Member.query.filter_by(group_id=this_group.group_id, user_id=user_id).first()
    return (this_group, this_member)

def get_select_list_for_members(member_list):
    '''
    Takes in a SQLAlchemy Query object containing Members, returns a list of (member_codename, member_realname)
    pairs to be used in a select_field.

    :param member_list:
    :return select_list:
    '''
    select_list = [(each_member.get_identity()['codename'], each_member.get_identity()['realname'])
                              for each_member in member_list]
    return select_list

###############################################
#---------------------------------------------#
# Error Handlers
#---------------------------------------------#
###############################################

@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500

@app.errorhandler(404)
def internal_error(error):
    return render_template('errors/404.html'), 404