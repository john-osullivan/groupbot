__author__ = 'John'

def get_groups_from_user(user):
    groups = user.memberships.group
    return groups