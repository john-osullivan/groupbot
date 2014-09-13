__author__ = 'John'
import csv
from groupbot.models import User, Group, Member, Role, db_session

NEW_OBJECTS = []

def create_tdc():
    tdc = Group(human_name="Theta Delta Chi", codename="tdc-mit")
    db_session.add(tdc)
    NEW_OBJECTS.append(tdc)
    db_session.commit()
    print "Okay, just made a Group called " + tdc.codename
    return tdc

def add_users(user_csv):
    '''
    Takes in a .csv of User information and then makes a bunch of Users out of it.  Returns them
    at the end.
    :param user_csv:
    :return:
    '''
    # First, make a list to hold all the Users we make so we can return it.
    new_users = []

    # Open up the .csv and make a reader to iterate through its rows
    with open(user_csv, 'rb') as user_file:
        user_data = csv.reader(user_file)

        # Pop off a row to get rid of the header.
        user_data.next()

        # Now, iterate through each row and create a User object
        for each_user in user_data:

            # Get the info from the row and use it to make a fresh User
            (codename, password, first_name, last_name, email, phone, bio, photo) = each_user
            new_user = User(codename=codename, password=password, first_name=first_name,
                            last_name=last_name, email=email, phone=phone)

            # Next, add 'em to the database session and the NEW_OBJECTS list.
            db_session.add(new_user)
            NEW_OBJECTS.append(new_user)
            new_users.append(new_user)

        # After that big loop, commit these Users so they have primary key IDs -- then return 'em.
        db_session.commit()
        print "Phew, just finished up making these " + str(len(new_users)) + " new Users over here."
        return new_users

def clean_up():
    '''
    Deletes all objects created in the population script, in order to make testing easier.
    :return:
    '''
    print "Deleting..."
    for thing in NEW_OBJECTS:
        print "... and " + str(thing)
        db_session.delete(thing)
    db_session.commit()
    print "... all done!\n"

def add_members(group, users):
    '''
    Takes all the Users and makes them Members in the Group.

    :param group:
    :param users:
    :return:
    '''

    # Okay -- to get started, iterate through all the Users
    for user in users:

        # Create a new Member object for each one
        new_member = Member(group_id=group.group_id, user_id=user.user_id, codename=user.codename)

        # Now add it into the db_session and the NEW_OBJECTS list.
        db_session.add(new_member)
        NEW_OBJECTS.append(new_member)

    # Finally, after having created all those Members, commit this ish.
    db_session.commit()
    print "Awesome, just made " + str(len(users)) + " Members in the " + group.codename + " group.\n"

def build_roles(group, role_csv):

    # First, open up the .csv of role data and make a reader for it.
    with open(role_csv, 'rb') as role_file:
        role_data = csv.reader(role_file)

        # Make a list to store all the new Roles so we can find out how many we made later on.
        new_roles = []

        # Pop off a row to get rid of the header, then start iterating through the file.
        role_data.next()
        for each_role in role_data:

            # Grab the data out of the row and make a new Role object out of it
            (role_name) = each_role
            new_role = Role(group_id=group.group_id, name=role_name)

            # Then add the role to the db_session, NEW_OBJECTS list, and new_roles list.
            db_session.add(new_role)
            NEW_OBJECTS.append(new_role)
            new_roles.append(new_role)

        # Finally, after having created all the Roles, commit and print something nice.
        db_session.commit()
        print "WHOA -- I just made " + str(len(new_roles)) + " new Roles.\n"

def populate_database(test=True):
    '''
    Creates a group for TDC, a user account for every brother, and Memberships.  It also creates Roles for all the
    officer positions and assigns at least one Member to each one.  It gets the information for User/Member accounts
    by reading in a .csv of values called user_data.csv and member_data.csv respectively.

    :return:
    '''

    print "Okay, let's get started with populating the database!\n"
    tdc = create_tdc()
    users = add_users('groupbot/static/csv/user_data.csv')
    add_members(tdc, users)
    build_roles(tdc, 'groupbot/static/csv/role_data.csv')

    if test:
        print "Okay, since this was just a test, I'm gonna delete all the shit I just made."
        clean_up()
    else:
        print "This was for real!  You just created " + len(NEW_OBJECTS) + " new things in the database."

if __name__ == '__main__':
    populate_database()