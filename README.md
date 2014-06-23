# Welcome
This is Bond, an online group organization platform being developed by John O'Sullivan and Harry Bleyan (not that we don't welcome help!).  In a sentence, it lets people bond into *Groups* which have *Members*.  These *Members* have *Roles*.  These *Roles* let them create and manage *Events*, give and receive *Tasks*, and contribute to the Role's *InfoPage*.  Groups can also *Bond* to other Groups, letting them share InfoPages and choose *Representatives* for each other's Groups.

Additionally, the platform is going to be expanded to support Discussions and Meetings.  In general, it will be expanded to support many more things -- the idea is in FLUX.  

This README is going to discuss:
- Backend Data Model
- Controller/View Functions
- Front-End Design Documentation
- Future Features/Dream Ideas

## Backend Data Model
The system currently recognizes eight SQLAlchemy models which correspond to database tables:
- Users
- Groups
- Bonds
- Members
- Roles
- Tasks
- Infopages
- Events
- (Pending) Representatives
- (Pending) Committees/InGroups
- (Pending) Meetings
- (Pending) Discussions

### Users
Users separated from the specific activity of each group.  All association is handled through members, allowing users to fluidly be a part of multiple groups.  It has the colums:
- Name (String)
- Email (Validated String)
- Phone Number (Optional)
- Bio (String)
- Members (Many to Many)
- Photo (Binary)
- memberships (relation to Members)

### Groups
Groups are collections of Members.  They also point to Roles and Tasks.  Eventually, a group there will be surrounding features like by-laws, voting, motions for updates, and a discussion system.  For now, however, it is expressed as a collection of people.  It has the columns:
- Display Name (String) : A non-unique name to refer to the group by, to make 
standard use easier.
- Code Name (String) : A unique name for the group similar to a Twitter handle
or Facebook URL.
- Members (One to Many)
- By-Line (String)
- Description (Long String)
- Roles (One to Many
- Tasks (One to Many)
It also inherits things from relationship backrefs, like:
- 'bonds'
- 

### Bonds
Bonds are designed to allow for cooperation between different groups.  They let Groups designate shared InfoPages, and they let them establish Representatives into each other.  For now, that's it.
- groups : relationship to Groups, meant to be only two groups.
- Representatives : relationship to Members.

### Members
A Member contains all the information a user would want to interact with in the group.  Specifically, members perform roles, have responsibilities, and gather points.  It has the columns:
- Preferred Name (Optional String)
- Role (Many to Many)
- Doing Tasks (Many to Many)
- Giving Tasks (Many to Many)
- Points (Integer)
It also inherits a great deal of properties from relationship backrefs, like:
- 'user'
- 'group'

### Roles
A role is part of a group, has a description, comes with some responsibilities, and also gives people the power to assign some types of responsibilities.  It also comes with a title, because of course.  The columns are:
- Name (Required String)
- Group (Foreign Key)
- Description (Long String)
- Doing Tasks (Many to Many)
- Giving Tasks (Many to Many)
Inherited from relationship backrefs:
- groups -> Group
- members -> Member


### Tasks
A task is the basic unit of getting things done.  They are hierarchical, such that any task can have sub-tasks.  If a task has points enabled, the points on its subtasks should always sum to an equal or lesser amount -- however, this constraint is not yet enforced.  They are equipped with double approval, first from the person who performed the task and second from the person who assigned it.  It also has a field for a due date, which will later be used to send text or email reminders.  It has a name, a description, a delivered Boolean (whether the doer says it is complete), an approved Boolean (whether the giver says it's complete), an optional due data, an optional points reward, and an optional comments section.  The columns are:
- Name (Short String)
- Description (Medium String)
- Due Date (DateTime)
- Delivered (Boolean)
- Approved (Boolean)
- Giver_ID (One-to-One Relationship to Member)
- Doer_ID (One-to-One Relationship to Member)
- Points (Integer)
- Comments (Short String)
- Parent_ID (ForeignKey Integer)
- Child (One-to-Many Relationship)
Inherited from relationship backrefs:
- groups -> Group

### Infopages
Infopages allow for quick display of relevant information about a group, description of roles or any additional supporting material.  The columns are:
- Title (Required String)
- Parent ID (Foreign Key)
- Description (150 character long String)
- Content (42420 character String) : Will need to be changed later
- Children (if any)

### Events
Events are a class for getting people to come to a particular place at a particular time. Events have a date, RSVP lists, location, description, name, duration and attended/missed people.
- name (String) - big name of the Event
- group_id -> Group which is hosting/owning the event.
- host - collection of additional people who can be added to host the event
- description (String) - Short description of the Event
- location (String) - Location of the event, if any
- start_time (DateTime) - The starting time of the event
- end_time (DateTime) - The ending of the event
- invited - collection of Members who were invited to the Event
- rsvp_yes - collection of members who RSVPd 'Yes'.
- rsvp_no - collection of members who RSVPd 'No'.
- attended_yes - collection of members who DID attend the event, as verified by the /attend function on events.  This is useful for roll call, quorum, etc.
- attended_no - collection of members who DIDN'T attend the event.
Inherited from relationship backrefs:


## UNIMPLEMENTED CLASSES

### Representatives
As of right now, a Representative is a dummy class whose only attributes are the Member ID and Bond ID.  It also has some properites descended from relationship backrefs, like:
- bond

### Discussions

### Meetings


## Controller/View Functions
I need to figure out what front-end pages are required to make this thing work.  For the basest functionality, you need to be able to make an account, create a group, join/leave a group.  Create roles, assign them to members, take them away, change who it's assigned to.  Create responsibilities in a template fashion, give roles the ability to give them out, have them be doable and reward members with points.  Speaking of points, I need to make a points logger -- it just needs to sit on the database class and record every transaction based on the group.  Actually, based on everything.  We should be able to pick apart that points log however we want, to allow for many different views from different privacy levels.

If I have all of that in there, though, I think I could make a sample group.  The concept of responsibilities as a template is important.  It makes a responsibility a standard type of thing you have to get done.

## Front-End Design Documentation
I haven't implemented it yet because I'm terrible!  Once I have each piece working such that shit can display, unit tests.  Unit tests for everyone.

### User Dashboard
The user's dashboard holds a summary of the activity from all of their memberships.  It collects the Roles and Tasks they have in each group, separating those they have to complete and those they need other people to complete.  It is essentially a gloss of all their commitments, only listing the titles.  Those titles link to the task's detail page.

### Group InfoPage
A group's page lists its name, by-line, and description.  Additionally, it should have a roster (list of all members), list of officers, and a listing of any group-wide responsibilities.  Any responsibility that is required of every member should be listed on this page with its percent completion by the brotherhood.  This would include things like attendance to meeting, clean-ups, and nightly duties.

### Member InfoPage
The member page includes all roles held, current responsibilities, points count and history.  Additionally, it can store a history of prior roles held and how they did in them (because why not?).  It also has different section for the responsibilities required of the member and the responsibilities checked by the member.

### Role InfoPage
The role's page holds its title, description, the responsibilities required of and distributed by, and a list of prior members who held that role.  It will later be expanded to include reports on how it went and how to do it, similar to a bible for each role.

### Task InfoPage


## Future Features
There are buckets of future functionality planned, including exhaustive Role-based Permissions, automated Task reminders, Google Drive/Docs integration, Facebook event integration, and more.

- THINGS: We need to have a single Table which lists every other entry in the database so we can uniquely identify them and determine what Permissions a specific Member should have on it.  
- We need Task and Event creation templating.  The Task creation screen should let you make a duplicate of a Task and only changing specific fields really easily, then automatically make the individual Tasks for each Member.  This would work best if it integrated with a Google Drive spreadsheet.
- PERMISSIONS: Everything is listed in a Table so we can determine what each Member's Permission is for that Thing. The potential permissions are should they be able to SEE/EDIT/CREATE/DELETE a InfoPage, Event, Task, whathaveyou.  Ideally, we want a piece of code which gets a Thing, Member, and action type, and we get back a boolean of whether or not it's authorized.
- There should be mulitple ways to "deliver" a deliverable, ranging from writing some text, signing your virtual name, uploading a photo or file, etc.  Expanding this really broadens the number of usecases for a Task.
- VOTES: There needs to be a built-in idea of a vote which goes to every Member and has a minimum satisfaction margin that is a variable property.  This should be able to flip easily between being a one minute vote to table a motion, or one week vote to decide between two option for an event.
- DISCUSS: We want a forum-style implementation that uses reddit voting combined with tagging to filter and sort the Discussion board into a legitimately useful place to talk shit with your Groups.
- POINTS: Groups have currencies.  There's always some way to measure how much someone is doing, and we need to represent that.  There should be potential Points attached to Tasks, and those Points should be able to be called whatever the Group wants.  Points needs to be able to have a refresh period determined, a Point at which they're tallied and collection begins once more.
- A reminder system which lets users assigning tasks specify a time for email and text message reminders to the person who has to do the task.
- Group templates!  Users should be able to say whether they're making a club, fraternity, sports team, project group, company, etc.