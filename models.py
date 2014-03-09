from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
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

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(30))
    phone = db.Column(db.Integer)
    bio = db.Column(db.String(160))
    photo = db.Column(db.LargeBinary)

    memberships = relationship("Membership", backref= 'users')


    def __init__(self, name=None, password=None, email=None, phone=None, \
                            bio=None, photo=None, memberships=None):
        self.name = name
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

    gp_id = db.Column(db.Integer, primary_key = True)

    partnerships = db.Column(db.Integer, db.ForeignKey('groups.group_id'), primary_key=True)
    partners = db.Column(db.Integer, db.ForeignKey('groups.group_id'), primary_key=True)

def __init__(self, partnerships=None, partners=None):
    self.partners = partners
    self.partnerships = partnerships

class Group(Base):
    __tablename__ = 'groups'

    group_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    byline = db.Column(db.String(160))
    description = db.Column(db.String(1024))

    members = relationship('Member', backref='groups')

    # Relations to establish non-hierarchical partnerships between groups.
    partnerships = relationship('GroupPartnership', backref='partners',\
                                                primaryjoin=id=GroupPartnership.partnerships)
    partners = relationship('GroupPartnership', backref='partnerships',\
                                                primaryjoin=id=GroupAffiliations.affiliations)

    # Relations to establish one-to-many parent-child relationships.
    parent_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'))
    children = relationship('Group', backref='parent')

    def __init__(self, name, byline=None, description=None, members=None,\
                        partnerships=None, partners=None, parent_id=None, children=None):
        self.name = name
        self.byline = byline
        self.description = description
        self.members = members
        self.partnerships = partnerships
        self.partners = partners
        self.parent_id = parent_id
        self.children = children

    def __repr__(self):
        return "Group #: %s --  Group Name: %s" % (self.group_id, self.name)


class Member(Base):
    __tablename__ = 'members'

    member_id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'), default=None, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), default=None, index=True)
    
    preferred_name = db.Column(db.String(80))
    points = db.Column(Integer)

    roles = relationship('Role', backref='members')
    responsibilities = relationship('Responsibility', backref='members')

    def __init__(self, preferred_name=None, points=None, roles=None, responsibilities=None):
        self.preferred_name = preferred_name
        self.points = points
        self.roles = roles
        self.responsibilities = responsibilities

    def __repr__(self):
        return "Member # of Group #: %s --- %s"%(self.member_id, self.group_id)

member_roles = Table(
    'member_roles', Base.metadata,
    db.Column('member_id', Integer, ForeignKey('members.member_id')),
    db.Column('role_id', Integer, ForeignKey('roles.role_id'))
    )

class Role(Base):
    __tablename__ = 'roles'

    # Bookkeping ids
    role_id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'), default=None, index=True, nullable=False)
    member_id = relationship('Member', secondary=member_roles)

    # Position information
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(2048))
    
    # Responsiblity organization of both those given to you and those you give out.
    given_resp_id = db.Column(db.Integer, db.ForeignKey('responsibilities.responsibility_id'))
    giving_resp_id = db.Column(db.Integer, db.ForeignKey('responsibilities.responsibility_id'))
    given_responsibilities = relationship('Responsibility', foreign_keys=[given_resp_id], backref='roles')
    giving_responsibilities = relationship('Responsibility', foreign_keys=[giving_resp_id], backref='roles')

    def __init__(self, group_id, member_id=None, name, description=None):
        self.group_id = group_id
        self.member_id = member_id
        self.name = name
        self.description = description

    def __repr__(self):
        return "Role #(%s) of Group #(%s) held by Member #(%s)"%(self.role_id, self.group_id, self.member_id)

class Responsibility(Base):
    __tablename__ = 'responsibilities'

    responsibility_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String(512))
    delivered = db.Column(db.Boolean, default=False)
    points = db.Column(db.Integer)
    comments = db.Column(db.String(256))

    group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'), backref='responsibilities', nullable=False)
    given_id = db.Column(db.Integer, db.ForeignKey('members.member_id'), backref='responsibilities', nullable=False)
    giver_id = db.Column(db.Integer, db.ForeignKey('members.member_id'), backref='responsibilities', nullable=False)

    given = relationship('Member', foreign_keys=[given_id])
    giver = relationship('Member', foreign_keys=[giver_id])

    def __init__(self, name=None, description=None, points=None, \
                        comments=None, given_id, giver_id, group_id):
        self.name = name
        self.description = description
        self.points = points
        self.comments = comments
        self.given_id = given_id
        self.giver_id = giver_id
        self.group_id = group_id

    def __repr__(self):
        return "Responsibility #(%s) of Group #(%s) held by Member #(%s)"%(self.responsibility_id, self.gr)

# Create tables.
Base.metadata.create_all(bind=engine)
