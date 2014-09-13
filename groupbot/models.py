from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.engine import reflection
from groupbot import db
import os
from config import SQLALCHEMY_DATABASE_URI

engine = create_engine(SQLALCHEMY_DATABASE_URI)
inspector = reflection.Inspector.from_engine(engine)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
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

# Helper function to validate if a table and ID pair point to a valid object
# in the database.  This validates both the table string and the object.  Currently
# still a method stub.
def is_real_thing(table, thing_id):
    if is_table(table):
        return tablename_to_class(table).query.get(thing_id) != None

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

    user_id = db.Column(db.Integer, primary_key=True)
    codename = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(32), nullable=False)
    first_name = db.Column(db.String(32))
    last_name = db.Column(db.String(32))
    email = db.Column(db.String(40), unique=True, nullable=False)
    phone = db.Column(db.Integer, unique=True)
    bio = db.Column(db.String(160))
    photo = db.Column(db.LargeBinary)

    memberships = db.relationship("Member", backref= 'user')


    def __init__(self, codename, password, first_name=first_name, last_name=last_name, email=None,
                 phone=None, bio=None, photo=None, memberships=None):
        self.first_name = first_name
        self.last_name = last_name
        self.codename = codename
        self.password = password
        self.email = email
        self.phone = phone
        self.bio = bio
        self.photo = photo
        self.memberships = memberships

    def __repr__(self):
        return "User #: %s"%(self.user_id)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.user_id)


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
    # NOTE: Not currently being used, as all group connection is being
    # handled by partnerships.
    parent_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'))
    children = db.relationship('Group', backref='parent', remote_side=[group_id])

    def __init__(self, human_name, codename, byline=None, description=None, members=[],\
                 parent_id=None):
        self.human_name = human_name
        self.codename = codename
        self.byline = byline
        self.description = description
        self.members = members
        self.parent_id = parent_id

    def __repr__(self):
        return "Group #: %s --  Group Name: %s" % (self.group_id, self.name)


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
    photo = db.Column(db.String(128))
    bio = db.Column(db.String(256))

    def __init__(self, group_id, user_id, codename, bio=None, photo=None):
        self.group_id = group_id
        self.user_id = user_id
        self.codename = codename
        self.bio = bio
        self.photo = photo

    def __repr__(self):
        return "Member # of Group #: %s --- %s"%(self.member_id, self.group_id)

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
    db.Column('member_id', Integer, ForeignKey('members.member_id')),
    db.Column('role_id', Integer, ForeignKey('roles.role_id'))
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

    def __init__(self, group_id, name, member_id=None, description=None):
        self.group_id = group_id
        self.member_id = member_id
        self.name = name
        self.description = description

    def __repr__(self):
        return "Role #(%s) of Group #(%s) held by Member #(%s)"%(self.role_id, self.group_id, self.member_id)

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
    db.Column('giving_member_id', Integer, ForeignKey('members.member_id')),
    db.Column('given_member_id', Integer, ForeignKey('members.member_id')),
    db.Column('task_id', Integer, ForeignKey('tasks.task_id'))
    )

member_delivering_tasks = db.Table(
    'member_delivering_tasks', Base.metadata,
    db.Column('delivering_member_id', Integer, ForeignKey('members.member_id')),
    db.Column('task_id', Integer, ForeignKey('tasks.task_id'))
)

member_approving_tasks = db.Table(
    'member_approving_tasks', Base.metadata,
    db.Column('approving_member_id', Integer, ForeignKey('members.member_id')),
    db.Column('task_id', Integer, ForeignKey('tasks.task_id'))
)

role_delivering_tasks = db.Table(
    'role_delivering_tasks', Base.metadata,
    db.Column('delivering_role_id', Integer, ForeignKey('roles.role_id')),
    db.Column('task_id', Integer, ForeignKey('tasks.task_id'))
)

role_approving_tasks = db.Table(
    'role_approving_tasks', Base.metadata,
    db.Column('approving_role_id', Integer, ForeignKey('roles.role_id')),
    db.Column('task_id', Integer, ForeignKey('tasks.task_id'))
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

    def __init__(self, name=name, group_id=group_id, start_time=None, end_time=None, host_member_id=None,
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
        if host_member_id is not None: self.host.append(Member.query.get(host_member_id))
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
# # UI Classes
# #---------------------------------------------#
# ###############################################
#
# group_infos_table = db.Table('group_infopages', Base.metadata,
#     db.Column('group_id', db.Integer, db.ForeignKey('groups.group_id')),
#     db.Column('infopage_id', db.Integer, db.ForeignKey('infopages.infopage_id'))
# )
#
# member_infos_table = db.Table('member_infopages', Base.metadata,
#     db.Column('member_id', db.Integer, db.ForeignKey('members.member_id')),
#     db.Column('infopage_id', db.Integer, db.ForeignKey('infopages.infopage_id'))
# )
#
# '''
# Stores the relations from Infopages to their main Infoblocks, the ones produced and
# laid out by us.
# '''
# main_infoblocks = db.Table(
#
#     'main_infoblocks', Base.metadata,
#     db.Column('infopage_id', Integer, ForeignKey('infopages.infopage_id')),
#     db.Column('infoblock_id', Integer, ForeignKey('infoblocks.infoblock_id'))
#     )
#
# '''
# This stores the relations to determine which Infoblocks have been created by users
# on which pages.  Just a straight up ID, no need to get fancy.
# '''
# user_infoblocks = db.Table(
#     'user_infoblocks', Base.metadata,
#     db.Column('infopage_id', Integer, ForeignKey('infopages.infopage_id')),
#     db.Column('infoblock_id', Integer, ForeignKey('infoblocks.infoblock_id'))
#     )
#
# class Infopage(Base):
#     __tablename__ = 'infopages'
#
#     '''
#     Infopages allow for quick display of relevant information about a group, description of roles
#     or any additional supporting material. Infopages are supposed to map to a group, a member, a user,
#     a role, a task another infopage or not have any host at all (i.e. help page for groupify).
#     For the developmental stage of groupify, Infopages shall be a massive container for HTML code that can
#     be modified and made links between. Later on, a custom set of templates will be created to simplify and
#     standardize the look of all the Infopage instances.
#
#     name = String(80) - big name of the Infopage
#     description = String(150) - Short description of the infopage
#     source_table = String(80) - String name of the table this Infopage points to
#     source_id = ForeignKey value for source_table, specifies host of this Infopage
#     content = String(42420) - The HTML holder for all the content
#     children = --> sub-infopages, if any
#
#     POTENTIAL REDESIGN:
#     Invert the way infopages are referenced.  Every info page has a String representing the name
#     of a table, and an integer ID representing which record in that table it's an Infopage for.
#     '''
#
#     infopage_id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(80), nullable=False)
#     end_view = db.Column(db.PickleType, nullable=False)
#
#     # These two properties completely describe what the item in database
#     source_table = db.Column(db.String(80), nullable=False)
#     source_id = db.Column(db.Integer, nullable=False)
#     description = db.Column(db.String(1024))
#
#     # Associations to Groups to make it easy to chunk Infopages by the Groups&Members
#     # which contribute to their construction. Note that the backref means
#     # Group&Member objects can use 'object.infopages' to get a Query
#     # of all their Infopages.
#     groups = db.relationship("Group", secondary=group_infos_table, backref='infopages')
#     contributors = db.relationship("Member", secondary=member_infos_table, backref='infopages')
#
#     # Relations to establish one-to-many parent-child db.relationships.
#     children = db.relationship('Infopage', backref='parent')
#
#     # Relations to the two categories of Infoblocks -- the main Infoblocks and the user  Infoblocks.
#     main_infoblocks = db.relationship("Infoblock", secondary=main_infoblocks, backref="infopage")
#     user_infoblocks = db.relationship("Infoblock", secondary=user_infoblocks, backref="infopage")
#
#     def __init__(self, name, end_view, source_table, source_id, description=None, content=None):
#         self.name = name
#         self.end_view = end_view
#         self.source_table = source_table
#         self.source_id =source_id
#         self.description = description
#         self.content = content
#
#     def __repr__(self):
#         return "Infopage #{0} -- {1} #{2} -- {3}".format(self.infopage_id, self.source_table,\
#                 self.source_id, self.name)
#
#     def source(self):
#         if is_real_thing(self.source_table, self.source_id):
#             return
#
#
# class Infoblock(Base):
#     __tablename__ = 'infoblocks'
#     '''
#     This class describes one "block" on an Infopage.  A block looks similar to one
#     Pinterest post.  It can take up 1, 2, or 3 thirds of the screen and has a variable
#     height (it's as tall as it needs to be).  Each Infoblock appears on one page,
#     they are not shared.  They are stored in an order, so they have an integer
#     describing their position.  Their actual content is HTML, stored as a sanitized
#     string.  Like other units, they also have a name.  Whether the Infoblock is
#     created by our system or created by users is stored in the content_type
#     attribute.
#
#     .name = String(80)
#     .width = Integer, 1 <= n <= 3
#     .content_func = Python function, the name of the view function which builds the 'content' object.
#     .infopage_id = Foreign Key to Infopage table
#     .order = Integer, n >= 0
#     .content_type = String(40)
#     .content = String(42420)
#     '''
#     infoblock_id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(80))
#     content_func = db.Column(db.PickleType(), nullable=False)
#     width = db.Column(db.Integer)
#     order = db.Column(db.Integer, nullable = False)
#     content_type = db.Column(db.String(40), nullable=False)
#     content = db.Column(db.String(4200))
#     template = db.Column(db.String(42420), nullable=False)
#
#     def __init__(self, order, content_func, content_type, template, \
#                     width=None,content=None, name=None):
#         self.name = name
#         self.content_func = content_func
#         self.width = width
#         self.order = order
#         self.template = template
#         self.content_type = content_type
#         self.content = content
#
#     def __repr__(self):
#         return "Infoblock #{0}: {1}".format(self.infoblock_id, self.name)
#
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
Base.metadata.create_all(bind=engine)