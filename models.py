from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from app import db

engine = create_engine('sqlite:///database.db', echo=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

# Set your classes here.

class User(Base):
    __tablename__ = 'users'

    '''
    Stores all users, gives a unique ID.  Allows for a name, email, password,
    phone number, 160 character biography, and a photo.  There is also a 
    one-to-many db.relationship with the Membership table, allowing each user
    to be a part of many groups.

    username = String(30), in-service name, unique and not nullable
    password = String(30), not nullable
    name = String(120), meant for real-world name, not unique
    email = String(120), unique
    phone = Integer, unique
    bio = String(160), super short self-description
    photo = LargeBinary, essentially a thumbnail to represent themselves
    memberships = -> Members, one-to-many, portal to all actual group management
    '''

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)
    name = db.Column(db.String(40))
    email = db.Column(db.String(40), unique=True)
    phone = db.Column(db.Integer, unique=True)
    bio = db.Column(db.String(160))
    photo = db.Column(db.LargeBinary)

    memberships = db.relationship("Member", backref= 'users')


    def __init__(self, username, password, name=None, email=None, phone=None, \
                            bio=None, photo=None, memberships=None):
        self.name = name
        self.username = username
        self.password = password
        self.email = email
        self.phone = phone
        self.bio = bio
        self.photo = photo
        self.memberships = memberships

    def __repr__(self):
        return "User #: %s"%(self.user_id)

class GroupPartnership(Base):
    __tablename__ = 'group_partnerships'

    '''
    GroupPartnership Table stores all the horizontal connections between groups.
    It has its own tables because groups are horizontally connected in a
    many-to-many db.relationship.  It takes two inputs to create a connection.  The
    partnerships field describes groups which contain this group (i.e. TDC has a
    representative at IFC).  The partners field describes groups which are contained
    by this group (i.e. IFC has a number of partners, one of which is TDC).
    '''

    gp_id = db.Column(db.Integer, primary_key = True)

    partnerships = db.Column(db.Integer, db.ForeignKey('groups.group_id'), primary_key=True)
    partners = db.Column(db.Integer, db.ForeignKey('groups.group_id'), primary_key=True)

    def __init__(self, partnerships=None, partners=None):
        self.partners = partners
        self.partnerships = partnerships

    def __repr__(self):
        return "Group Partnership #{0}".format(self.gp_id)

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
    code_name = db.Column(db.String(80), unique=True, nullable=False)
    byline = db.Column(db.String(160))
    description = db.Column(db.String(2048))

    members = db.relationship('Member', backref='groups')
    tasks = db.relationship('Task', backref='groups')
    roles = db.relationship('Role', backref='groups')

    # Relations to establish non-hierarchical partnerships between groups.
    partnerships = db.relationship('GroupPartnership', backref='partners', primaryjoin=id==GroupPartnership.partnerships)
    partners = db.relationship('GroupPartnership', backref='partnerships', primaryjoin=id==GroupPartnership.partners)

    # Relations to establish one-to-many parent-child db.relationships.
    # NOTE: Not currently being used, as all group connection is being
    # handled by partnerships.
    parent_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'))
    children = db.relationship('Group', backref='parent')

    def __init__(self, human_name, code_name, byline=None, description=None, members=None,\
                        parent_id=None, children=None):
        self.human_name = human_name
        self.code_name = code_name
        self.byline = byline
        self.description = description
        self.members = members
        self.parent_id = parent_id
        self.children = children
        self.roles = None

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
    points = Integer - If a points sytem is in use, this is their running total.
    roles = --> Role, many-to-many, established by member_roles table
    doing_tasks = --> Task, one-to-many, describes tasks assigned TO the member
    giving_tasks = --> Task, one-to-many, describes tasks assigned BY the member
    '''

    member_id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'), default=None, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), default=None, index=True)
    
    preferred_name = db.Column(db.String(80))
    points = db.Column(Integer)

    roles = db.relationship('Role', backref='members')
    doing_tasks = db.relationship('Task', backref='members')
    giving_tasks = db.relationship('Task', backref='members')

    def __init__(self, group_id, preferred_name=None, points=None, roles=None):
        self.group_id = group_id
        self.preferred_name = preferred_name
        self.points = points
        self.roles = roles

    def __repr__(self):
        return "Member # of Group #: %s --- %s"%(self.member_id, self.group_id)

member_roles = db.Table(
    '''
    Handles the many-to-many db.relationship between members and roles, allowing for
    a role to have performed by multiple members or have one member perform 
    multiple roles.
    '''
    'member_roles', Base.metadata,
    db.Column('member_id', Integer, ForeignKey('members.member_id')),
    db.Column('role_id', Integer, ForeignKey('roles.role_id'))
    )

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
    member_id = db.relationship('Member', secondary=member_roles)

    # Position information
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(2048))
    
    # Responsiblity organization of both those given to you and those you give out.
    doing_task_id = db.Column(db.Integer, db.ForeignKey('tasks.task_id'))
    giving_task_id = db.Column(db.Integer, db.ForeignKey('tasks.task_id'))
    doing_tasks = db.relationship('Task', foreign_keys=[doing_task_id], backref='roles')
    giving_tasks = db.relationship('Task', foreign_keys=[giving_task_id], backref='roles')

    def __init__(self, group_id, name, member_id=None, description=None):
        self.group_id = group_id
        self.member_id = member_id
        self.name = name
        self.description = description

    def __repr__(self):
        return "Role #(%s) of Group #(%s) held by Member #(%s)"%(self.role_id, self.group_id, self.member_id)

member_tasks = db.Table(
    '''
    Table which handles the db.relationship between members and tasks.  Our goal is to have
    two members associated with each task, one who is giving it and one who is doing it.  The
    table has three columns, one for the giving_member_id, one for the doing_member_id, and
    one for the task_id.
    '''
    'member_tasks', Base.metadata,
    db.Column('giving_member_id', Integer, ForeignKey('members.member_id')),
    db.Column('given_member_id', Integer, ForeignKey('members.member_id')),
    db.Column('task_id', Integer, ForeignKey('tasks.task_id'))
    )

class Task(Base):
    __tablename__ = 'tasks'

    '''
    Tasks are the unit of gettings things done in the system.  They are meant to
    map to precisely two members: the member who assigned it and the member
    who is doing it.  Tasks are hierarchical, so a task can have subtasks.  
    All subtasks of a task should have their points values sum to no
    greater than the parent task, but that constraint is not yet enforced in the
    system.  A task given to every member in a role should actually 
    create a large number of sub-tasks for each member to individually complete.

    name = String(80) - Should just be a title
    description = String(512) - Fuller description of what should typically be done
    due_at = DateTime - The date/time at which this task is due.  To be used for reminders...
    delivered = Boolean - Whether the doer says they've finished the task
    approved = Boolean - Whether the giver says the task was fully satisfied
    points = Integer - Number of  points the task is worth
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
    delivered = db.Column(db.Boolean, default=False)
    approved = db.Column(db.Boolean, default=False)
    points = db.Column(db.Integer)
    comments = db.Column(db.String(256))

    # Relations to establish one-to-many parent-child db.relationships.
    parent_id = db.Column(db.Integer, db.ForeignKey('tasks.task_id'))
    children = db.relationship('Task', backref='parent')

    group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'), nullable=False)
    doing_id = db.Column(db.Integer, db.ForeignKey('members.member_id'), nullable=False)
    giving_id = db.Column(db.Integer, db.ForeignKey('members.member_id'), nullable=False)
 
    doer = db.relationship('Member', foreign_keys=[doing_id], secondary=member_tasks)
    giver = db.relationship('Member', foreign_keys=[giving_id], secondary=member_tasks)

    def __init__(self, name, doer_id, giver_id, group_id, description=None, points=None, \
                        comments=None):
        self.name = name
        self.description = description
        self.points = points
        self.comments = comments
        self.doing_id = doer_id
        self.giving_id = giver_id
        self.group_id = group_id

    def __repr__(self):
        return "Task #(%s) of Group #(%s) held by Member #(%s)"%(self.task_id, self.group_id, self.doing_id)

class Infopage(Base):
    __tablename__ = 'infopages'

    '''
    Infopages allow for quick display of relevant information about a group, description of roles
    or any additional supporting material. Infopages are supposed to map to a group, a member, a user,
    a role, a task another infopage or not have any parent at all (i.e. help page for groupify).
    For the developmental stage of groupify, Infopages shall be a massive container for HTML code that can
    be modified and made links between. Later on, a custom set of templates will be created to simplify and 
    standardize the look of all the Infopage instances.

    title = String(80) - big title of the Infopage
    description = String(150) - Short description of the infopage
    parent_xxx_id = ForeignKey of any other class type xxx, points to the parent of this Infopage
    content = String(42420) - The HTML holder for all the content
    children = --> sub-infopages, if any
    '''

    infopage_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(150))
    content = db.Column(db.String(42420))

    # Relations to establish one-to-many parent-child db.relationships.
    children = db.relationship('Infopage', backref='parent')


    # One of these should be non-null. The great variety of classes is there because different things might
    # require infopages
    parent_group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'))
    parent_task_id = db.Column(db.Integer, db.ForeignKey('tasks.task_id'))
    parent_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    parent_role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'))
    parent_member_id = db.Column(db.Integer, db.ForeignKey('members.member_id'))
    parent_gp_id=db.Column(db.Integer, db.ForeignKey('group_partnerships.gp_id'))

    def __init__(self, title, parent_group_id=None, parent_task_id=None, parent_user_id=None, parent_role_id=None, \
                        parent_member_id=None, parent_gp_id=None, content=None, description=None):
        self.title = title
        self.parent_group_id = parent_group_id
        self.parent_task_id = parent_task_id
        self.parent_user_id = parent_user_id
        self.parent_role_id = parent_role_id
        self.parent_member_id = parent_member_id
        self.parent_gp_id = parent_gp_id
        self.description = description
        self.content=content

        # This bit is for the __repr__ function that comes right after - to be able to display readable parameters,
        # you need to be able to see what the parent of the Infopage is, and the parent's id.
        if parent_group_id!=None:
            self.parent_human_name="Group"
            self.parent_human_id=parent_group_id
        elif parent_member_id!=None:
            self.parent_human_name="Member"
            self.parent_human_id=parent_member_id
        elif parent_role_id!=None:
            self.parent_human_name="Role"
            self.parent_human_id=parent_role_id
        elif parent_task_id!=None:
            self.parent_human_name="Task"
            self.parent_human_id=parent_task_id
        elif parent_user_id!=None:
            self.parent_human_name="User"
            self.parent_human_id=parent_user_id
        elif parent_gp_id!=None:
            self.parent_human_name="Partnership"
            self.parent_human_id=parent_gp_id
        else:
            self.parent_human_name="Solitary"
            self.parent_human_id=0


    def __repr__(self):
        return "%s Infopage #(%s). Parent: %s #(%s)"%(self.parent_human_name, self.infopage_id, \
                self.parent_human_name, self.parent_human_id)


# Create tables.
Base.metadata.create_all(bind=engine)
