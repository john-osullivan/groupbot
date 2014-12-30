# Welcome
This is GroupBot, an online community organization platform.  It's designed to make organizing a group
of people to achieve a common goal easier to do.  For now, it does that by letting users:
* Join into *Groups* as *Members* (note the distinction from *Users*).  
* Take on *Roles*, which organize *Members* by their function in the group, as well as compile all the information 
related to performing said Role in one place.
* Give and receive *Tasks* which are first assigned by an assigner, then delivered by the assigned, and finally approved by the assigner.
* Invite other Members & Roles to *Events*, as well as take attendance for that event. 

Some key next steps will be to incorporate *Committees* as internal subgroups, *Representatives* to connect different 
groups, and forum-style *Discussions* which will mimic mailing lists.   

This README documents the underlying data model supporting the application.

## Backend Data Model
The system currently recognizes eight SQLAlchemy models which correspond to database tables:
- Users
- Groups
- Bonds
- Members
- Roles
- Tasks
- Events
- (Pending) Representatives
- (Pending) Committees
- (Pending) Discussions

### Users
Users separated from the specific activity of each group.  All association is handled through members, allowing users to fluidly be a part of multiple groups.  It has the columns:
- first_name (String)
- last_name (String)
- codename (String) - Unique identifier, essentially a username.
- email (Validated String)
- phone (Optional String)
- bio (String, 160 characters)
- photo (LargeBinary)
- memberships (relation to Members)

### Groups
Groups are collections of Members.  They also have relationships to Roles, Tasks, and Events.  Groups have the columns:
- human_name (String) : A non-unique name for the group, easily changeable.
- codename (String) : A unique name for the group, similar to a Twitter handle or Facebook URL.
- byline (String, 160 characters) : A blurb about the Group, akin to a User's bio
- description (Long String) : A longer and more thorough description of what the Group is and how it works.  Currently
capped at 2048 characters, likely to change.
- members (One to Many relation to Member)
- roles (One to Many relation to Role)
- tasks (One to Many relation to Task)
- events (One to Many relation to Event)

### Members
A Member contains all the information a user would want to interact with in the group.  Specifically, Members perform Roles, give/receive Tasks, host/attend Events, and edit InfoPages.  It has the columns:
- codename (String, 80 characters) : Members have their own unique codenames, so a User can decide how they want to be 
referred to within a Group.
- bio (String, 160 characters) : Member-specific bio, for information just related to this Group.
- photo (LargeBinary) : A photo just to be used within this Group on the Member profile.
- roles (Many to Many relationship to Roles) : 
- delivering_tasks (Many to Many relationship to Task) : Tasks which this Member must deliver (Tasks assigned *to* them).
- approving_tasks (Many to Many relationship to Task) : Tasks which this Member must approve (Tasks assigned *by* them).
- hosting_events (Many to Many relationship to Event) : Events this Member is hosting.
- invited_events (Many to Many relationship to Event) : Events this Member is invited to.
- rsvp_yes_events (Many to Many relationship to Event) : Events this Member RSVPd *yes* to.
- rsvp_no_events (Many to Many relationship to Event) : Events this Member RSVPd *no* to.
- attended_events (Many to Many relationship to Event) : Events this Member attended.

### Roles
A Role is part of a group, can be held by multiple Members, has a description, can both give and receive Tasks, 
and can host or be invited to an Event.  The columns are:
- name (Required String, 80 characters) : Name for Role, not unique.
- description (String, 2048 characters) : Description of Role, meant to contain all the key information about it.
- delivering_tasks (Many to Many relationship to Task) : Tasks which some Member who has this Role must deliver (Tasks assigned *to* them).
- approving_tasks (Many to Many relationship to Task) : Tasks which some Member who has this Role must approve (Tasks assigned *by* them).
- hosting_events (Many to Many relationship to Event) : Events this Role is hosting.
- invited_events (Many to Many relationship to Event) : Events this Role is invited to.

### Tasks
A Task is the basic unit of getting things done.  They are hierarchical, meaning any task can have sub-tasks.  
A Task is assigned by one Member or Role to another Member or Role.  Those assigned to complete a Task deliver it, then
the assigner approves it.  It has a deadline, which will later be used for text or email reminders.  For describing the
Task itself, it has a name, description, and comments -- each are Strings.  There is a Deliverable field which is 
currently a String (meant to be the Member's signature saying they completed it), but will be changed to be a LargeBinary
to allow for arbitrary file upload.  The columns are:
- name (String, 80 characters) : What's the Task called?
- description (String, 512 characters) : What does the Task require?
- comments (String, 256 characters) : Any additional comments that might vary from one otherwise similar Task to another.
- deadline (DateTime) : When is the Task due by?
- deliverable (String, 256 characters) : This is whatever the Task needed the deliverer to produce.  For now, it's a
String because I don't know how to make file upload work right.  Eventually, however, it will take file upload so people
 can upload arbitrary files (images, pdfs, etc) to fulfill a Task.
- delivered (Boolean) : Has the Task been delivered yet?  If multiple people can deliver it, it's marked as delivered
once the first person delivers it.
- delivering_members (Many-to-Many relationship to Member) : All the Members who are supposed to deliver the Task. 
- delivering_roles (Many-to-Many relationship to Role) : All the Roles whose Members are supposed to deliver the Task. 
- approved (Boolean) : Was the Task approved by the approver yet?
- approving_members (Many-to-Many relationship to Member) : All the Members who can approve the Task after delivery.
- approving_roles (Many to Many relationship to Role) : All the Roles whose Members can approve the Task after delivery.
- parent_ID (ForeignKey to Task) : This Task's parent.
- children (One-to-Many Relationship to Task) : All of this Task's child Tasks.


### Events
Events are in the strictest sense, a way to invite Members & Roles to go to some place at some time and then take 
attendance of who showed up. Events have a start/end time, RSVP lists, location, description, name, and attendance list.
- name (String, 80 characters) : Name of the Event.
- description (String, 2000 characters) : A description of the Event, would include any and all details.
- location (String, 200 characters) : Location of the event, if any.  May use Geo datatype later, just a String for now.
- start_time (DateTime) : The starting time of the event.
- end_time (DateTime) : The ending of the event.
- hosting_roles (Many to Many relationship to Role) : All Roles with host privileges (can edit & invite) to the Event.
- hosting_members (Many to Many relationship to Member) : All Members with host privileges to the Event.
- invited_roles (Many to Many relationship to Role) : All Roles whose Members are invited to attend the Event.
- invited_members (Many to Many relationship to Member) : All Members who are invited to attend the Event.
- rsvp_yes (Many to Many relationship to Member) : All invited Members who RSVP'd yes.  Note that a members stays in 
the invited pool even once they have RSVP'd.
- rsvp_no (Many to Many relationship to Member) : All invited Members who RSVP'd no.
- attended (Many to Many relationship to Member) : All invited Members who were marked as in attendance.  Note that we 
don't need a not_attended relationship because those Members can be inferred from this one.


## UNIMPLEMENTED CLASSES

### Representatives

### Committees

### Discussions

### Meetings



## Future Features
There are buckets of future functionality planned, including exhaustive Role-based Permissions, automated Task reminders, Google Drive/Docs integration, Facebook event integration, and more.

- People are essentially getting Events and Tasks as notification type things, along with all the other
  cool shit that's coming. Discussions and meetings are the two biggest things that'd flesh this out.
  Style points for plug and play GroupMe + Google Groups mirroring functionality...
- THINGS: We need to have a single Table which lists every other entry in the database so we can uniquely identify them and determine what Permissions a specific Member should have on it.  
- We need Task and Event creation templating.  The Task creation screen should let you make a duplicate of a Task and only changing specific fields really easily, then automatically make the individual Tasks for each Member.  This would work best if it integrated with a Google Drive spreadsheet.
- PERMISSIONS: Everything is listed in a Table so we can determine what each Member's Permission is for that Thing. The potential permissions are should they be able to SEE/EDIT/CREATE/DELETE a InfoPage, Event, Task, whathaveyou.  Ideally, we want a piece of code which gets a Thing, Member, and action type, and we get back a boolean of whether or not it's authorized.
- There should be mulitple ways to "deliver" a deliverable, ranging from writing some text, signing your virtual name, uploading a photo or file, etc.  Expanding this really broadens the number of usecases for a Task.
- VOTES: There needs to be a built-in idea of a vote which goes to every Member and has a minimum satisfaction margin that is a variable property.  This should be able to flip easily between being a one minute vote to table a motion, or one week vote to decide between two option for an event.
- DISCUSS (older): We want a forum-style implementation that uses reddit voting combined with tagging to filter and sort the Discussion board into a legitimately useful place to talk shit with your Groups.
- DISCUSS (newer): This idea is more functional, getting something hammered out that works with what everyone's already using.
- Alternate DISCUSS: One easy tie-in implementation is to simply make a Google Group for each actual Group, enabling an email address for each separate Group someone has (conditional settings, brah).
- Small-scale DISCUSS: People also need text groups, always.  Different setups, whatever the fuck.  The group should be able to have up to a certain number of GroupMes and then start charging (because I'm sure the API will eventually).  Each one is a "pinned thread" on the votable bulletin board.  The email threads move, these don't.
- POINTS: Groups have currencies.  There's always some way to measure how much someone is doing, and we need to represent that.  There should be potential Points attached to Tasks, and those Points should be able to be called whatever the Group wants.  Points needs to be able to have a refresh period determined, a Point at which they're tallied and collection begins once more.
- A reminder system which lets users assigning tasks specify a time for email and text message reminders to the person who has to do the task.
- Group templates!  Users should be able to say whether they're making a club, fraternity, sports team, project group, company, etc.