__author__ = 'John'

import os
import sys
import unittest
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

sys.path.append('../..')
from groupbot import app, db
from config import TEST_DATABASE_URI
from groupbot.models import db_session, User, Group, Member, Role, Task, Event, Base



class TestCase(unittest.TestCase):

    def use_test_database(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = TEST_DATABASE_URI
        self.app = app.test_client()
        db.metadata.create_all(db.engine)

    def empty_test_data(self):
        db.metadata.drop_all(db.engine)

    def setUp(self):
        self.use_test_database()

    def tearDown(self):
        self.empty_test_data()

    def make_admin(self):
        if User.query.filter_by(codename='admin').first() is not None:
            admin = User(codename='admin',password='letmein', first_name="THE",
                         last_name="ADMIN", email="j.osullivan42@gmail.com",
                         phone='0123456789', bio='This is the administrator account.')
            db_session.add(admin)
            db_session.commit()

    def make_test_group(self):
        self.login()
        new_group = Group(
            codename='test_group',
            human_name='The Test Group',
            byline="Whatever it is, I'm testing it.",
            description=""
            )
        db_session.add(new_group)
        db_session.commit()

    def login(self):
        self.make_admin()
        return self.app.post('/users/login', data=dict(
            codename='admin',
            password='letmein'
        ), follows_redirects = True)

    def logout(self):
        return self.app.get('/users/logout', follows_redirects=True)

    def test_user_create(self):
        create_response = self.app.post('/users/', data = dict(
            first_name = 'first_name',
            last_name = 'last_name',
            codename = 'codename',
            password = 'password',
            confirm = 'confirm',
            email = 'email@thetest.com',
            phone = '0123456789',
            photo = None,
            bio = "I'm a test account."
        ))
        print create_response
        assert "You just create an account called codename!  Glad to have you, thanks for joining." \
               in create_response.data
        assert User.query.all().count() > 0

    def test_user_edit(self):
        self.make_admin()
        params = dict(
            codename = 'new_codename',
            email = 'new_email',
            first_name = 'new_first_name',
            last_name = 'new_last_name',
            phone = '9876543210',
            photo = '',
            bio = 'This is the new thing I think about myself!"'
        )
        edit_response = self.app.post('/users/admin/edit', data=params)
        print edit_response
        assert "You successfully edited your user page!" in edit_response.data
        assert User.query.filter_by(codename = "new_codename").bio == "This is the new thing I think about myself!"

    def test_user_delete(self):
        self.make_admin()
        params = dict(
            delete = True
        )
        delete_response = self.app.post('/users/admin/delete', data=params)
        print delete_response
        assert "We're sad to see you go, admin :(" in delete_response.data
        assert User.query.all().count() == 0

class GroupTestCase(TestCase):
    def setUp(self):
        super(GroupTestCase, self).use_test_database()
        super(GroupTestCase, self).login()

    def tearDown(self):
        super(GroupTestCase, self).empty_test_data()

    def test_group_create(self):
        params = dict(
            codename = 'new_group',
            human_name = 'The Test Group',
            byline = 'Testing since November 10th, 2014.',
            description = ''
        )
        create_response = self.app.post('/groups/create', data=params)
        assert "You successfully created a group called The Test Group!" in create_response.data
        assert Group.query.filter_by(codename='new_group').first().human_name == "The Test Group"

    def test_group_edit(self):
        super(GroupTestCase, self).make_test_group()
        params = dict(
            human_name = "New Test Group",
            codename = "new_test_group",
            byline = "WHOA, WHAT JUST CHANGED GUYS?",
            description = "I'm not sure, but I might have a description now.",
        )
        edit_resposne = self.app.post('/groups/test_group/edit', data=params)
        print edit_resposne
        assert "You successfully edited new_test_group!"
        assert Group.query.filter_by(codename='new_test_group').first().human_name == "New Test Group"

    def test_group_delete(self):
        super(GroupTestCase, self).make_test_group()
        params = dict(
            delete = True
        )
        delete_response = self.app.post('/groups/test_group/delete', data=params)
        print delete_response
        assert "You successfully deleted test_group." in delete_response
        assert Group.query.all().count() == 0

class MemberTestCase(TestCase):
    def setUp(self):
        super(MemberTestCase, self).use_test_database()
        super(MemberTestCase, self).make_test_group()

    def tearDown(self):
        super(MemberTestCase, self).empty_test_data()

    def test_member_create(self):
        # We automatically have an admin user who is in the test group, but we need to make
        # up another one for the admin to invite into the test group.
        buddy = User(
            codename="test_user",
            password="test_password",
        )
        db_session.add(buddy)
        db_session.commit()

        # With that done, let's move on to adding them into the test group with a Member join request.
        params = dict(
            user_codename='test_user'
        )
        create_response = self.app.post('/groups/test_group/members/add', data=params)
        assert "Alright, you just added test_user to test_group!" in create_response
        assert len(Group.query.filter_by(group_codename='test_group').members) == 2

    def test_member_edit(self):
        params = dict(
            codename = 'new_member_codename',
            bio = "This is my new bio.",
            photo = None
        )
        edit_response = self.app.post('/groups/test_group/members/admin/edit', data=params)
        assert "Score!  You just successfully edited your Membership, new_member_codename." in edit_response
        assert Member.query.filter_by(codename='new_member_codename').first().bio == "This is my new bio."

    def test_member_delete(self):
        params = dict(
            delete = True
        )
        delete_response = self.app.post('/groups/test_group/members/admin/delete', data=params)
        assert "Okay, admin isn't a part of test_group anymore.  Bye! :(" in delete_response
        assert len(Group.query.filter_by(group_codename='test_group').members) == 0

if __name__ == '__main__':

    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = TEST_DATABASE_URI
    Base.query = db.session.query_property()
    # unittest.main()
    print 'db.metadata.drop_all(db.engine):'
    # db.metadata.drop_all(db.engine)
    print 'db.metadata.create_all(db.engine):'
    db.metadata.create_all(bind = 'testing')
    print 'Base.metadata.create_all(db.engine):'
    Base.metadata.create_all(db.engine)
    print 'db.session: '
    print db.session
    print '[user.codename for user in db.session.query(User).all()]:'
    print [user for user in db.session.query(User).all()]
    print db.engine