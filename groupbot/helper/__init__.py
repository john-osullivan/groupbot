__author__ = 'John'
from groupbot.models import Group

def get_groups_from_user(user):
    groups = [Group.query.get(membership.group_id) for membership in user.memberships]
    return groups