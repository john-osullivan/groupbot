__author__ = 'John'

from flask import Flask, request, session, g, redirect, url_for,\
     abort, render_template, flash, make_response
from flask.ext.sqlalchemy import SQLAlchemy,Pagination
from app import app
from models import db_session, User, Group, Member, \
                                Role, Task, Bond, \
                                Event, User, Infopage,\
                                Infoblock


__all__ = ['group', 'user', 'member', 'role', 'task', 'event']
#----------------------------------------------------------------------------#
# Helper Methods (that span across many functions).
#----------------------------------------------------------------------------#
def get_group_member(request):
    group = Group.query.get(request.POST['group_id'])
    member = Member.query.get(request.POST['member_id'])
    return (group, member)

##############################################
#----------------------------------------------------------------------------#
# Data Manipulators.
#----------------------------------------------------------------------------#
##############################################

# @app.route('/bond/create')
# def create_bond():
#     '''
#     INPUT
#     Requires the two group's IDs to be in the request, formatted as:
#     request['groups'] = [group1_id, group2_id]
#
#     OUTPUT
#     Creates the object in the database.  The Bond initializier handles the creation of
#     necessary associations in the foreign key.
#     '''
#
#     # Get the IDs encoded in the request.
#     (group1_id, group2_id) = request.POST['groups']
#
#     # Give them to the Bond initializer, then add and save the new Bond.
#     new_bond = Bond(group1_id, group2_id)
#     db_session.add(new_bond)
#     db_session.commit()
#     return True
#
# @app.route('/bond/<int:bond_id>/delete')
# def delete_bond(bond_id):
#     '''
#     INPUT
#     Takes the IDs of the Bond being deleted from the URL.  Needs to find the group_ids in
#     the Bond encoded in the request (same syntax as create), for validation's sake.
#
#     (Once there's a Permission's system built in, it should also take the Member's ID
#     to make sure they have Permission to make that action.)
#
#     OUTPUT
#     Deletes the object
#     '''
#     (group1_id, group2_id) = request.POST['groups']
#     group1 = Group.query.get(group1_id)
#     group2 = Group.query.get(group2_id)
#     dead_bond = Bond.query.get(bond_id)
#     bond_groups = dead_bond.groups
#     if (group1 in bond_groups) and (group2 in bond_groups):
#         db_session.delete(dead_bond)
#         db_session.commit()
#         return True
#     else:
#         raise Exception("The group's specified weren't part of the Bond to be deleted!")
#










# #----------------------------------------------------------------------------#
# # Infopages.
# #----------------------------------------------------------------------------#
# @app.route('/info/create')
# def create_infopage():
#     '''
#     INPUT
#     Member object in the request, in order to check that Permissions are valid.
#     Additionally a validated InfoPageForm.
#
#     RESULT
#     Infopage is created, the function returns True if everything goes well.  If
#     something breaks, it'll throw an Exception.
#     '''
#     # First, grab the Group and Member creating the InfoPage to do some validation.
#     (group, member) = get_group_member(request)
#
#     if member in group.members:
#         # Pull in the requried paramters of the InfoPage
#         source_table = request.form['page_source']['table_name']
#         source_id = request.form['page_source']['table_id']
#         page_name = request.form['page_name']
#
#         # Pull in the optional ones
#         if request.form['description'] != "": description = request.form['description'] \
#                                         else: description = None
#
#         # Create our friendly new InfoPage and save it in.
#         new_page = Infopage(page_name, source_table, source_id, description, content)
#         db_session.add(new_page)
#         db_session.commit()
#         return True
#     else:
#         raise Exception("That Member isn't part of that Group, they can't make a page for it!")
#
#
# @app.route('/info/<int:info_id>/delete')
# def delete_infopage(info_id):
#     '''
#     INPUT
#     Member object in the request, in order to check that Permissions are valid.  Additionally,
#     the ID of an InfoPage that needs to get deleted.
#
#     RESULT
#     Infopage is deleted, it returns True if all goes well -- otherwise it
#     throws an Exception.
#     '''
#     # First, grab the Group and Member creating the InfoPage to do some validation.
#     (group, member) = get_group_member(request)
#
#     # This is a sanity check for now, and it will eventually be upgraded to a full call to the
#     # Permissions authorizer to make sure this Member has the authority to perform this Action.
#     if member in group.members:
#         # Get the InfoPage, delete it, save our work.
#         info_id = request.POST['infopage_id']
#         infopage = Infopage.query.get(info_id)
#         db_session.delete(infopage)
#         db_session.commit()
#         return True
#     else:
#         raise Exception("The Member isn't part of the Group, they can't delete one of its Infopages!")
#
# @app.route('/info/<int:info_id>/edit')
# def edit_infopage(info_id):
#     '''
#     INPUT
#     The request will have a hash called 'infopage'.  The 'infopage' hash contains
#     the parameters 'name', 'description', 'main_infoblock_ids', 'user_infoblock_ids',
#     and 'children_ids'.  The first two parameters are strings, the second two are
#     arrays of integers representing the infoblock, infoblock, and infopage ids
#     respectively.
#
#     RESULT
#     Infopage has its name and descrption updated, any children are added to the
#     association, and the infoblock relationships are updated.
#     '''
#     # First, grab the Group, Member, and Infopage to do some validation.
#     (group, member) = get_group_member(request)
#     infopage = Infopage.query.get(info_id)
#
#     # Validate that the Member is part of the Group, all that jazz.
#     if member in group.members:
#
#         # Grab all the parameters from the request in String/array form
#         new_name = request.form['page_name']
#         new_description = request.form['page_description']
#         children_ids = request.POST['infopage']['children_ids']
#         main_infoblock_ids = request.POST['infopage']['main_infoblock_ids']
#         user_infoblock_ids = request.POST['infopage']['user_infoblock_ids']
#
#         # Turn the id arrays into lists of actual database objects
#         children = [Infopage.query.get(int(info_id))] for info_id in children_ids]
#         main_blocks = [Infoblock.query.get(int(info_id)) for info_id in main_infoblock_ids]
#         user_blocks = [Infoblock.query.get(int(info_id)) for info_id in user_infoblock_ids]
#
#         # Get the current sets for each relationship
#         current_children = infopage.children
#         current_main_blocks = infopage.main_infoblocks
#         current_user_blocks = infopage.user_infoblocks
#
#         # Modify the page's information
#         infopage.name = new_name
#         infopage.description = new_description
#
#         # Update each of our relationships
#         for child in children:
#             if child not in current_children:
#                 infopage.children.append(child)
#
#         for main_block in main_blocks:
#             if main_block not in current_main_blocks:
#                 infopage.main_infoblocks.append(main_block)
#
#         for user_block in user_blocks:
#             if user_block not in current_user_blocks:
#                 infopage.user_infoblocks.append(user_block)
#
#         # And save our work!
#         db_session.commit()
#
#         return True
#     else:
#         raise Exception("That Member isn't part of the group")
#
#
# #----------------------------------------------------------------------------#
# # Infoblock C/U/D functions.  Meant to act as internal functions, not URL
# # endpoints as of yet.  The create and edit Infopage functions will use these
# # editing Infoblocks function
# #----------------------------------------------------------------------------#
# def create_infoblock():
#     '''
#     INPUT
#     A request with a hash called 'infoblock'.  Within that hash, definitely
#     include the parameters infopage_id, width, order, content_type, and content.
#     Optionally also include a name.  Additionally, the group_id and member_id should all
#     be in the request.  The request should have the parameter 'create' in it when
#     we're trying to save the object.
#
#     RESULT
#     A new Infoblock is created in the database, and therefore rendered on the
#     Infopage.  Ideally, the user creates one or more blocks with Javascript and
#     then all the information required to save them in the database gets sent here.
#     '''
#     # First, grab the Group and Member.
#     (group, member) = get_group_member(request)
#
#     # If we're actually doing a create (never know if we're just rendering the page!)...
#     if request.POST['create']:
#
#         # Grab all of the mandatory Infoblock parameters from the request.
#         infopage_id = request.POST['infoblock']['infopage_id']
#         infopage = Infopage.query.get(infopage_id)
#         width = int(request.POST['infoblock']['width'])
#         order = int(request.POST['infoblock']['order'])
#         content_type = request.POST['infoblock']['content_type']
#         content = request.POST['infoblock']['content']
#
#         # Grab the optional name
#         if request.POST['infoblock']['name']: name = request.POST['infoblock']['name'] else: name = None
#
#         # Then use them to make an actual Infoblock
#         new_infoblock = Infoblock(name, width, order, content_type, content)
#
#         # Add the Infoblock to the Infopage's correct Infoblock relation
#         if content_type == 'main':
#             infopage.main_infoblocks.append(new_infoblock)
#         else if content_type == 'user':
#             infopage.user_infoblocks.append(new_infoblock)
#         else:
#             raise Exception("The infoblock's content_type isn't set to main or user!")
#         return True
#
# def edit_infoblock(infoblock_id, width, order, content, name):
#     '''
#     INPUT
#     A request with a hash called 'infoblock' and a parameter called 'update' which
#     is set to true when the acutal update is being processed.  Inside of the
#     'infoblock' hash, there should be an 'infopage_id', 'width', 'order', and 'content'.
#     Essentially the same thing as in the create function, right?  Additionally, the
#     request has the group_id and member_id.
#
#     RESULT
#     Find the infoblock in question, update each of its parameters.  Das it.
#     '''
#     # First, grab the Group, Member, and Infoblock in question.
#     (group, member) = get_group_member(request)
#     infoblock = Infoblock.query.get(infoblock_id)
#
#     # Now modify the actual properties and save the work
#     infoblock.width = width
#     infoblock.order = order
#     infoblock.content = content
#     infoblock.name = name
#     db_session.commit()
#     return True
#
# def delete_infoblock(infoblock_id):
#     '''
#     INPUT
#     An infoblock_id representing the one to be deleted.
#
#     RESULT
#     The block got DELETED, yo.  Also we returned True.  If the
#     '''
#     # First, grab the Group, Member, and Infoblock in question.
#     (group, member) = get_group_member(request)
#     infoblock = Infoblock.query.get(infoblock_id)
#     db_session.delete(infoblock)
#     db_session.commit()
#     return True

#----------------------------------------------------------------------------#
# Representatives.
#----------------------------------------------------------------------------#


#----------------------------------------------------------------------------#
# Committee.
#----------------------------------------------------------------------------#

