from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey,DateTime
from sqlalchemy.engine import reflection
from sqlalchemy.schema import DropConstraint, DropTable
from groupbot import app, db
import os

from flask.ext.login import LoginManager, current_user

login_manager = LoginManager()
login_manager.init_app(app)
inspector = reflection.Inspector.from_engine(db.engine)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=db.engine))
Base = declarative_base()
Base.query = db_session.query_property()



###############################################
#---------------------------------------------#
# Helper Functions.
#---------------------------------------------#
###############################################
# Helper function to convert a string table name to a reference to the class.
# This mostly allows us to be a little more fluid with how we get a class when
# we want to make a query on it. Currently still a method stub.
def tablename_to_class(table_string):
    return NAMES_TO_CLASSES[table_string]

# Helper function to validate whether a table string is valid -- meaning if
# it's one of our tablenames.
def is_table(table_string):
    print inspector.get_table_names
    return table_string in inspector.get_table_names()

def drop_shit():
    metadata = Base.metadata
    conn = db.engine.connect()
    metadata.reflect(bind=db.engine)
    # db.drop_all(bind=[engine])
    print "About to try and drop all foreign keys"
    for table in metadata.tables.values():
        for each_key in table.constraints:
            print each_key
            conn.execute(DropConstraint(each_key))

    print "About to try and drop all tables"
    for table in metadata.tables.values():
        print table.name
        print table.foreign_keys
        conn.execute(DropTable(table))

    print "Here are all our leftover tables"
    print metadata.tables.keys()

def db_DropEverything(db):
    # From http://www.sqlalchemy.org/trac/wiki/UsageRecipes/DropEverything

    conn=db.engine.connect()

    # the transaction only applies if the DB supports
    # transactional DDL, i.e. Postgresql, MS SQL Server
    trans = conn.begin()

    inspector = reflection.Inspector.from_engine(db.engine)

    # gather all data first before dropping anything.
    # some DBs lock after things have been dropped in
    # a transaction.
    metadata = Base.metadata

    tbs = []
    all_fks = []

    for table_name in inspector.get_table_names():
        fks = []
        for fk in inspector.get_foreign_keys(table_name):
            if not fk['name']:
                continue
            fks.append(
                db.ForeignKeyConstraint((),(),name=fk['name'])
                )
        t = db.Table(table_name,metadata,*fks)
        tbs.append(t)
        all_fks.extend(fks)

    for fkc in all_fks:
        conn.execute(db.DropConstraint(fkc))

    for table in tbs:
        conn.execute(db.DropTable(table))

    trans.commit()


###############################################
#---------------------------------------------#
# User + Group + Member Models
#---------------------------------------------#
###############################################

class User(Base):
    __tablename__ = 'users'

    '''
    Stores all users, gives a unique ID.  Allows for a name, email, password,
    phone number, 160 character biography, and a photo.  There is also a 
    one-to-many db.relationship with the Membership table, allowing each user
    to be a part of many groups.

    code_name = String(32), in-service name, unique and not nullable.  It's supposed
                        to act almost like a Twitter handle for the user.
    password = String(32), not nullable
    first_name = String(32), first real-world name
    last_name = String(32), last real-world name
    email = String(120), unique
    phone = Integer, unique
    bio = String(160), super short self-description
    photo = LargeBinary, essentially a thumbnail to represent themselves
    memberships = -> Members, one-to-many, portal to all actual group management
    '''

    user_id = db.Column(db.BigInteger, primary_key=True)
    codename = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(32), nullable=False)
    first_name = db.Column(db.String(32))
    last_name = db.Column(db.String(32))
    email = db.Column(db.String(40), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True)
    bio = db.Column(db.String(160))
    photo = db.Column(db.LargeBinary)

    memberships = db.relationship("Member", backref= 'user')


    def __init__(self, codename, password, first_name=None, last_name=None, email=None,
                 phone=None, bio=None, photo=None):
        self.first_name = first_name
        self.last_name = last_name
        self.codename = codename
        self.password = password
        self.email = email
        self.phone = phone
        self.bio = bio
        self.photo = photo

    def __repr__(self):
        return "User #{0}".format(self.user_id)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.user_id)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.context_processor
def add_user():
    return {current_user : current_user}

class Group(Base):
    __tablename__ = 'groups'

    '''
    Groups are the fundamental building block of the system.  Each one has a
    name, byline (160 character description), and full description.  Groups also
    contain members.  Every task assigned in a group is tied to that group via 
    a one-to-many relation.  Groups can be connected vertically or horizontally.
    A vertical connection implies a hierarchy -- TDC at MIT is a child of 
    TDC National.  A horizontal connection implies a partnership -- TDC at MIT
    cooperates with MIT IFC to help make Greek life better for everyone.

    code_name = String(80)
    human_name = String(80)
    byline = String(160)
    description = String(1024)
    members = --> Member, one-to-many
    tasks = --> Task, one-to-many
    partnerships = --> Group, many-to-many, describes non-hierarchical groups
                                this group is a member of
    partners = --> Group, many-to-many, describes non-hierarchical groups that
                            are a part of this group
    parent_id = ForeignKey(Group), each group has at most one parent group
    children = --> Group, one-to-many, each group can have as many children
                            groups as it wants
    '''

    group_id = db.Column(db.Integer, primary_key=True)
    human_name = db.Column(db.String(80), nullable=False)
    codename = db.Column(db.String(80), unique=True, nullable=False)
    byline = db.Column(db.String(160))
    description = db.Column(db.String(2048))

    members = db.relationship('Member', backref='group')
    tasks = db.relationship('Task', backref='group')
    roles = db.relationship('Role', backref='group')
    events = db.relationship('Event', backref='group')
   
    # Relations to establish one-to-many parent-child db.relationships.
    parent_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'))
    children = db.relationship('Group', backref='parent', remote_side=[group_id])

    def __init__(self, human_name, codename, byline=None, description=None,\
                 parent_id=None):
        self.human_name = human_name
        self.codename = codename
        self.byline = byline
        self.description = description
        self.parent_id = parent_id

    def __repr__(self):
        return "Group #: {0} --  Group Name: {1}".format(self.group_id, self.codename)


class Member(Base):
    __tablename__ = 'members'

    '''
    Members populate Groups.  All activites in the group correspond with the Member object, freeing
    the User from any specific Group interaction.  Each Member object has foreign keys to the group
    it's a part of and the user it is for.

    group_id = ForeignKey Integer to Group, many-to-one
    user_id = ForeignKey Integer to User, many-to-one
    preferred_name = String(80) - If the User wants to be known different in this context
    roles = --> Role, many-to-many, established by member_roles table
    doing_tasks = --> Task, one-to-many, describes tasks assigned TO the member
    giving_tasks = --> Task, one-to-many, describes tasks assigned BY the member
    '''

    member_id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'), default=None, index=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), default=None, index=True, nullable=False)
    codename = db.Column(db.String(80), nullable=False)
    photo = db.Column(db.LargeBinary)
    bio = db.Column(db.String(160))

    def __init__(self, group_id, user_id, codename, bio=None, photo=None):
        self.group_id = group_id
        self.user_id = user_id
        self.codename = codename
        self.bio = bio
        self.photo = photo

    def __repr__(self):
        return "Member #{0} of Group #{1}".format(self.member_id, self.group_id)

    def get_realname(self):
        user = User.query.get(self.user_id)
        return user.first_name + " " + user.last_name

    def get_identity(self):
        '''
        Returns a dictionary with the Member's realname
        '''
        return {'realname':self.get_realname(), 'id':self.member_id, 'codename':self.codename}

    def get_by_codename(self,codename,groupname):
        '''

        '''
        this_group = Group.query.filter_by(codename=groupname).first()
        return Member.query.filter_by(codename=codename, group_id=this_group.group_id).first()
'''
Handles the many-to-many db.relationship between members and roles, allowing for
a role to have performed by multiple members or have one member perform 
multiple roles.
'''
member_roles = db.Table(
    'member_roles', Base.metadata,
    db.Column('member_id', db.Integer, ForeignKey('members.member_id')),
    db.Column('role_id', db.Integer, ForeignKey('roles.role_id'))
    )


###############################################
#---------------------------------------------#
# Group work: Roles/Tasks/Events
#---------------------------------------------#
###############################################


class Role(Base):
    __tablename__ = 'roles'

    '''
    Roles are the medium by which members can give or take on tasks.  Essentially, it represents
    any position in a group where you are given specific duties.  It has a name and
    description, and two many-to-many db.relationships with Tasks.  One db.relationship is for the Tasks
    assigned to the Role, the other is for Tasks assigned by the role.

    group_id = ForeignKey Group, many-to-one
    member_id = --> Member, many-to-many, so that one role can be performed by multiple people
    name = String(80), not nullable
    description = String(2048), to give people room to write out a decent description
    '''

    # Bookkeping ids
    role_id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'), index=True, nullable=False)
    members = db.relationship('Member', secondary=member_roles, backref='roles')

    # Position information
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(2048))

    def __init__(self, group_id, name, description=None):
        self.group_id = group_id
        self.name = name
        self.description = description

    def __repr__(self):
        return "Role #{0} of Group #{1}".format(self.role_id, self.group_id)

    def update_member_tasks(self):
        '''
        Same story as update_member_invites, except to work for Tasks.
        '''
'''
Table which handles the db.relationship between members and tasks.  Our goal is to have
two members associated with each task, one who is giving it and one who is doing it.  The
table has three columns, one for the giving_member_id, one for the doing_member_id, and
one for the task_id.
'''
member_tasks = db.Table(
    'member_tasks', Base.metadata,
    db.Column('giving_member_id', db.Integer, ForeignKey('members.member_id')),
    db.Column('given_member_id', db.Integer, ForeignKey('members.member_id')),
    db.Column('task_id', db.Integer, ForeignKey('tasks.task_id'))
    )

member_delivering_tasks = db.Table(
    'member_delivering_tasks', Base.metadata,
    db.Column('delivering_member_id', db.Integer, ForeignKey('members.member_id')),
    db.Column('task_id', db.Integer, ForeignKey('tasks.task_id'))
)

member_approving_tasks = db.Table(
    'member_approving_tasks', Base.metadata,
    db.Column('approving_member_id', db.Integer, ForeignKey('members.member_id')),
    db.Column('task_id', db.Integer, ForeignKey('tasks.task_id'))
)

role_delivering_tasks = db.Table(
    'role_delivering_tasks', Base.metadata,
    db.Column('delivering_role_id', db.Integer, ForeignKey('roles.role_id')),
    db.Column('task_id', db.Integer, ForeignKey('tasks.task_id'))
)

role_approving_tasks = db.Table(
    'role_approving_tasks', Base.metadata,
    db.Column('approving_role_id', db.Integer, ForeignKey('roles.role_id')),
    db.Column('task_id', db.Integer, ForeignKey('tasks.task_id'))
)

class Task(Base):
    __tablename__ = 'tasks'

    '''
    Tasks are the unit of gettings things done in the system.  They are meant to
    map to precisely two members: the member who assigned it and the member
    who is doing it.  Tasks are hierarchical, so a task can have subtasks.  A task
    given to every member in a role should actually create a large number of 
    sub-tasks for each member to individually complete.

    name = String(80) - Should just be a title
    description = String(512) - Fuller description of what should typically be done
    due_at = DateTime - The date/time at which this task is due.  To be used for reminders...
    delivered = Boolean - Whether the doer says they've finished the task
    approved = Boolean - Whether the giver says the task was fully satisfied
    comments = String(256) - Field for comments as needed
    parent_id = ForeignKey Task, points to the parent of this task_id
    children = --> Task, one-to-many to sub-tasks
    group_id = ForeignKey Group, points to the group this task was assigned as
                        a part of
    doing_id = ForeignKey Member, points to the member who is responsible for
                        completing the task
    giving_id = ForeignKey Member, points to the member who assigned the task
                        and is responsible for checking it
    '''

    task_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(512))
    deadline = db.Column(db.DateTime)
    deliverable = db.Column(db.String(256))
    delivered = db.Column(db.Boolean, default=False)
    approved = db.Column(db.Boolean, default=False)
    comments = db.Column(db.String(256))

    # Relations to establish one-to-many parent-child db.relationships.
    parent_id = db.Column(db.Integer, db.ForeignKey('tasks.task_id'))
    children = db.relationship('Task', backref='parent', remote_side=[task_id])

    group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'), nullable=False, index=True)

    delivering_members = db.relationship('Member', secondary=member_delivering_tasks, backref='delivering_tasks',
                                         post_update=True)
    approving_members = db.relationship('Member', secondary=member_approving_tasks, backref='approving_tasks',
                                        post_update=True)

    delivering_roles = db.relationship('Role', secondary=role_delivering_tasks,backref='delivering_tasks',
                                       post_update=True)
    approving_roles = db.relationship('Role', secondary=role_approving_tasks,backref='approving_tasks',
                                      post_update=True)

    def __init__(self, name, group_id, description=None, deadline=None, deliverable=None,
                 comments=None):
        self.name = name
        self.group_id = group_id
        self.description = description
        self.deliverable = deliverable
        self.comments = comments
        self.delivered = False
        self.approved = False

    def __repr__(self):
        return "Task #(%s) of Group #(%s) held by Member #(%s)"%(self.task_id, self.group_id, self.delivering_member_id)

    def is_late(self):
        return ((DateTime.now() > self.deadline) and (self.delivered == False))

    def is_delivering(self, member):
        return member in self.delivering_members

    def is_approving(self, member):
        return member in self.approving_members

    def update_deliverers_by_roles(self):
        '''
        Updates all the Members in the .delivering_members relation based upon which Members have delivering_roles.
        '''
        if self.delivering_roles is not None:
            for each_member in self.group.members:
                delivering = True if len(set(self.delivering_roles) & set(each_member.roles)) > 0 else False
                if delivering and each_member not in self.delivering_members:
                    self.delivering_members.append(each_member)
                elif not delivering and each_member in self.delivering_members:
                    self.delivering_members.remove(each_member)

    def update_approvers_by_roles(self):
        '''
        Updates all the Members in the .approving_members relation based on which Members have approving_roles.
        '''
        if self.approving_roles is not None:
            for each_member in self.group.members:
                approving = True if len(set(self.approving_roles) & set(each_member.roles)) > 0 else False
                if approving and each_member not in self.approving_members:
                    self.approving_members.append(each_member)
                elif not approving and each_member in self.approving_members:
                    self.approving_members.remove(each_member)


member_host_table = db.Table('event_hosts', Base.metadata,
    db.Column('event_id', db.Integer, db.ForeignKey('events.event_id')),
    db.Column('member_id', db.Integer, db.ForeignKey('members.member_id'))
)

member_invite_table = db.Table('event_invites', Base.metadata,
    db.Column('event_id', db.Integer, db.ForeignKey('events.event_id')),
    db.Column('member_id', db.Integer, db.ForeignKey('members.member_id'))
)

member_rsvp_yes_table = db.Table('event_rsvp_yes', Base.metadata,
    db.Column('event_id', db.Integer, db.ForeignKey('events.event_id')),
    db.Column('member_id', db.Integer, db.ForeignKey('members.member_id'))
)

member_rsvp_no_table = db.Table('event_rsvp_no', Base.metadata,
    db.Column('event_id', db.Integer, db.ForeignKey('events.event_id')),
    db.Column('member_id', db.Integer, db.ForeignKey('members.member_id'))
)

member_attend_table = db.Table('event_attend_yes', Base.metadata,
    db.Column('event_id', db.Integer, db.ForeignKey('events.event_id')),
    db.Column('member_id', db.Integer, db.ForeignKey('members.member_id'))
)

role_host_table = db.Table('event_role_host', Base.metadata,
    db.Column('event_id', db.Integer, db.ForeignKey('events.event_id')),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.role_id'))
)

role_invite_table = db.Table('event_role_invite', Base.metadata,
    db.Column('event_id', db.Integer, db.ForeignKey('events.event_id')),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.role_id'))
)

class Event(Base):
    __tablename__ = 'events'

    '''
    Events are a class for getting people to come to a particular place at a particular time.
    Events have a date, RSVP lists, location, description, name, duration and attended/missed people.

    name = String(80) - big name of the Event
    description = String(150) - Short description of the Event
    creator_id = ForeignKey - Original creator of the event
    date = DateTime - the date and time of the event
    duration = DateTime - the duration of the event
    rsvp_yes/rsvp_no - collection of members who are RSVPing yes or no
    attended_yes/attended_no - collection of member who attended or not
    location = String(200) - location of the event, if any
    host - collection of additional people who can be added to host the event

    '''

    # A couple of parameters defining the different unique characteristics of an event type
    event_id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'), nullable=False, index=True)

    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(2000))
    start_time = db.Column(db.DateTime())
    end_time = db.Column(db.DateTime())
    # TODO: Look for a "Geo" data-type to use for location.
    location = db.Column(db.String(200))

    # Boolean settings: these change how the Event is managed.
    visible_to_uninvited = db.Column(db.Boolean, default=True)
    invited_can_invite = db.Column(db.Boolean, default=False)

    # The ROLE relationships!
    hosting_roles = db.relationship('Role', backref='hosting_events', secondary=role_host_table, post_update=True)

    invited_roles = db.relationship('Event', backref='invited_events', secondary=role_invite_table, post_update=True)

    ## ALL OF THE FOREIGN KEYS TO THE MEMBER TABLE.  SO MANY MUHFUCKIN' RELATIONSHIPS.
    ## Hosts are the Members with the ability to edit the Event and take attendance.
    hosting_members = db.relationship('Member', backref='hosting_events', secondary=member_host_table, post_update=True)

    ## List of people invited to the event
    invited_members = db.relationship('Member', backref='invited_events', secondary=member_invite_table, post_update=True)

    ## People's responses to the event will be recorded here
    rsvp_yes = db.relationship('Member', backref='rsvp_yes_events', secondary=member_rsvp_yes_table, post_update=True)
    rsvp_no = db.relationship('Member', backref='rsvp_no_events', secondary=member_rsvp_no_table, post_update=True)

    ## List of people who attended the event.  We don't need to explicitly represent the list of those
    ## who didn't, since it's just the "other side" of this list.  It can be generated on-the-fly.
    attended = db.relationship('Member', backref='attended_events', secondary=member_attend_table, post_update=True)

    def __init__(self, name=name, group_id=group_id, start_time=None, end_time=None,
                 description=None, location=None, visible_to_uninvited=True,
                 invited_can_invite=False):
        self.name = name
        self.description = description
        self.start_time=start_time
        self.end_time=end_time
        self.location=location
        self.visible_to_uninvited = visible_to_uninvited
        self.invited_can_invite = invited_can_invite
        Group.query.get(group_id).events.append(self)
        if visible_to_uninvited is not None: self.visible_to_uninvited = visible_to_uninvited
        if invited_can_invite is not None: self.invited_can_invite = invited_can_invite

    def __repr__(self):
        return "Event #(%s) created by Member #(%s)"%(self.event_id, self.creator_id)

    def already_happened(self):
        return DateTime.now() > self.start_time

    def attended_by(self, member):
        return member in self.attended

    def attendance_taken(self):
        return self.attended is not None

    def get_noshows(self):
        no_shows = [each_member for each_member in self.invited_members if not self.attended_by(each_member)]
        return no_shows

    def is_invited(self, member):
        return member in self.invited_members

    def is_host(self, member):
        return member in self.hosting_members

    def no_rsvp(self, member):
        if (member in self.invited_members) and (member not in self.rsvp_yes) and (member not in self.rsvp_no):
            return True

    def can_invite(self, member):
        if self.invited_can_invite and member in self.invited_members:
            return True
        elif member in self.hosting_members:
            return True
        else:
            return False

    def member_can_see(self, member):
        '''
        This function makes it easy for the view to figure out if a given Member should be able to see
        that an Event is happening.  Logically, it first checks if the Event is visible Group-wide
        (aka has a True value in self.visible_to_uninvited).  If it *isn't* visible Group-wide, it
        checks if the member is hosting it or invited to it.  If one of those conditions is True, it
        returns True.  Otherwise, FALSE.
        '''
        if self.visible_to_uninvited:
            return True
        elif (member in self.host) or (member in self.invited_members):
            return True
        else:
            return False

    def update_invited_by_roles(self):
        # Run a check through every possible Member in the Group.  Should they be invited based on their Roles?
        for each_member in Group.query.get(self.group_id).members:

            # Assume they aren't invited until they are.
            invited = False
            for each_role in each_member.roles:

                # Once we know they're invited, flip the Boolean and stop iterating.
                if each_role in self.invited_roles:
                    invited = True
                    break

            # If invited is true, make sure their invited_events property includes this one
            if invited and each_member not in self.invited_members:
                self.invited_members.append(each_member)
                db_session.add(each_member)
            elif not invited and each_member in self.invited_members:
                self.invited_members.remove(each_member)
                db_session.add(each_member)

        # With all the Members that should be invited invited and all those that shouldn't be not,
        # commit the db_session and return the event.
        db_session.commit()

    def update_hosts_by_roles(self):
        '''
        We perform this by going through every Member, checking if they have one of the Roles that will
        make them an Event host, and then adding them or removing them based on the results of that.
        '''

        for each_member in Group.query.get(self.group_id).members:

            # Initially assume they're not hosting.
            hosting = False
            for each_role in self.hosting_roles:

                # Unless the turn out to have one of the hosting Roles, then say they are and break.
                if each_role in each_member.roles:
                    hosting = True
                    break

            # If it turns out they are but the system doesn't reflect that, make them a host.
            if hosting and each_member not in self.hosting_members:
                self.hosting_members.append(each_member)

            # If they aren't but it still thinks they are, fix that.
            elif not hosting and each_member in self.hosting_members:
                self.hosting_members.remove(each_member)

        # Just save our work and we're done.
        db_session.commit()


# ###############################################
# #---------------------------------------------#
# # Disorganized stubs.
# #---------------------------------------------#
# ###############################################
#
# class Representative(Base):
#     __tablename__ = 'representatives'
#     '''
#     A table containing information unique to a Representative.  Which group are they from,
#     which group are they representing in.  Also a string describing how it's chosen -- elected
#     or appointed.
#     '''

#     def __init__(self):

#     def __repr__(self):

# # class Committee(Base):
# #     __tablename__ = 'committees'
# #     '''
# #     A table containing the internal sub-groupings.  A committee is a Group which is meant
# #     to be purely internal to another Group.  It can't Bond with Groups other than its host,
# #     and it shares all InfoPage access with the host group.  It is only separate because it
# #     allows for special functionality of smaller, lighter sub-spaces within the larger Group
# #     space.
# #     '''
# #     def __init__(self):
#
# #     def __repr__(self):
#
# # class Discussion(Base):
# #     __tablename__ = 'discussions'
# #     '''
# #     '''
# #     def __init__(self):
#
# #     def __repr__(self):
#
NAMES_TO_CLASSES = {
    'users': User,
    'groups' : Group,
    'members' : Member,
    'roles' : Role,
    'tasks' : Task,
    'events' : Event
}

# Create tables.
Base.metadata.create_all(bind=db.engine)