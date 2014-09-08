__author__ = 'John'

from groupbot.models import User, Group, Member


def create_tdc():
    tdc = Group()
    return tdc

def add_users(user_csv):
    pass

def add_members(group, users):
    pass

def build_roles(group, role_csv):
    pass

def populate_database():
    '''
    Creates a group for TDC, a user account for every brother, and Memberships.  It also creates Roles for all the
    officer positions and assigns at least one Member to each one.  It gets the information for User/Member accounts
    by reading in a .csv of values called user_data.csv and member_data.csv respectively.

    :return:
    '''

    tdc = create_tdc()
    users = add_users('user_data.csv')
    add_members(tdc, users)
    build_roles(tdc, 'role_data.csv')

if __name__ == '__main__':
    populate_database()