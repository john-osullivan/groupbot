__author__ = 'John'
import csv
from groupbot.models import User, Group, Member, db_session

NEW_OBJECTS = []

def create_tdc():
    tdc = Group(human_name="Theta Delta Chi", codename="tdc-mit")
    db_session.add(tdc)
    db_session.commit()
    return tdc

def add_users(user_csv):

    # Open up the .csv and make a reader to iterate through its rows
    with open(user_csv, 'rb') as user_file:
        user_data = csv.reader(user_file)

        # Pop off a row to get rid of the header.
        user_data.next()

        # Now, iterate through each row and create a User object
        for each_user in user_data:

            # Get the info from the row, use it to make a fresh User, and add 'em to the NEW_OBJECTS list
            (codename, password, first_name, last_name, email, phone) = each_user
            new_user = User(codename=codename, password=password, first_name=first_name,
                            last_name=last_name, email=email, phone=phone)
            NEW_OBJECTS.append(new_user)

def add_members(group, users):
    pass

def build_roles(group, role_csv):
    pass

def populate_database(test=True):
    '''
    Creates a group for TDC, a user account for every brother, and Memberships.  It also creates Roles for all the
    officer positions and assigns at least one Member to each one.  It gets the information for User/Member accounts
    by reading in a .csv of values called user_data.csv and member_data.csv respectively.

    :return:
    '''

    tdc = create_tdc()
    users = add_users('static/csv/user_data.csv')
    add_members(tdc, users)
    build_roles(tdc, 'static/csv/role_data.csv')

    if not test:
        for new_thing in NEW_OBJECTS:
            db_session.add(new_thing)
        db_session.commit()

if __name__ == '__main__':
    populate_database()