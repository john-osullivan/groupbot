# Welcome
This is Groupify, a cloud-based group management platform.  In a sentence, it lets people make *groups* which have *members* who perform *roles* which have and distributed *responsibilities*.  Those responsibilities can optionally be worth points.  Groups can also connect to other groups in a hierarchy (i.e. a fraternity is a child of its national organization) or in partnership (i.e. a fraternity works with its school's IntraFraternity Council).  The system is being prototyped for a fraternity, so the examples throughout will correlate to that structure.

For now, it talks about the database back-end, then the functionality front-end, then current/next things to work on and build.

## Database Schema
The system recognizes five underlying objects which correspond to database tables:
- Users
- Groups
- Members
- Roles
- Tasks

### Users
Users separated from the specific activity of each group.  All association is handled through members, allowing users to fluidly be a part of multiple groups.  It has the colums:
- Name (String)
- Email (Validated String)
- Phone Number (Optional)
- Bio (String)
- Members (Many to Many)
- Photo (Binary)

### Groups
Groups are collections of members.  They also hold roles.  Eventually, a group will exist with surrounding features like by-laws, motions for updates, and a discussion system.  For now, however, it is expressed as a collection of people.  It has the columns:
- Human Name (String) : A non-unique name to refer to the group by, to make 
standard use easier.
- Code Name (String) : A unique name for the group similar to a Twitter handle
or Facebook URL.
- Members (One to Many)
- By-Line (String)
- Description (Long String)
- Roles (One to Many)
- Responsibilities (One to Many)

### Members
A Member contains all the information a user would want to interact with in the group.  Specifically, members perform roles, have responsibilities, and gather points.  It has the columns:
- Preferred Name (Optional String)
- Role (Many to Many)
- Doing Tasks (Many to Many)
- Giving Tasks (Many to Many)
- Points (Integer)

### Roles
A role is part of a group, has a description, comes with some responsibilities, and also gives people the power to assign some types of responsibilities.  It also comes with a title, because of course.  The columns are:
- Name (Required String)
- Group (Foreign Key)
- Description (Long String)
- Doing Tasks (Many to Many)
- Giving Tasks (Many to Many)


### Tasks
Lastly, a task is the basic unit of getting things done.  They are hierarchical, such that any task can have sub-tasks.  If a task has points enabled, the points on its subtasks should always sum to an equal or lesser amount -- however, this constraint is not yet enforced.  They are equipped with double approval, first from the person who performed the task and second from the person who assigned it.  It also has a field for a due date, which will later be used to send text or email reminders.  It has a name, a description, a delivered Boolean (whether the doer says it is complete), an approved Boolean (whether the giver says it's complete), an optional due data, an optional points reward, and an optional comments section.  The columns are:
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


## Front-End Functionality
I need to figure out what front-end pages are required to make this thing work.  For the basest functionality, you need to be able to make an account, create a group, join/leave a group.  Create roles, assign them to members, take them away, change who it's assigned to.  Create responsibilities in a template fashion, give roles the ability to give them out, have them be doable and reward members with points.  Speaking of points, I need to make a points logger -- it just needs to sit on the database class and record every transaction based on the group.  Actually, based on everything.  We should be able to pick apart that points log however we want, to allow for many different views from different privacy levels.

If I have all of that in there, though, I think I could make a sample group.  The concept of responsibilities as a template is important.  It makes a responsibility a standard type of thing you have to get done.

### User Dashboard
The user's dashboard holds a summary of the activity from all of their memberships.  It collects the Roles and Tasks they have in each group, separating those they have to complete and those they need other people to complete.  It is essentially a gloss of all their commitments, only listing the titles.  Those titles link to the task's detail page.

### Group Page
A group's page lists its name, by-line, and description.  Additionally, it should have a roster (list of all members), list of officers, and a listing of any group-wide responsibilities.  Any responsibility that is required of every member should be listed on this page with its percent completion by the brotherhood.  This would include things like attendance to meeting, clean-ups, and nightly duties.

### Member Page
The member page includes all roles held, current responsibilities, points count and history.  Additionally, it can store a history of prior roles held and how they did in them (because why not?).  It also has different section for the responsibilities required of the member and the responsibilities checked by the member.

### Role Page
The role's page holds its title, description, the responsibilities required of and distributed by, and a list of prior members who held that role.  It will later be expanded to include reports on how it went and how to do it, similar to a bible for each role.

### Responsibility Page
The responsibility page needs to display the name, description, optional points reward, comments, and whether or not it has been delivered.  Additionally, it should have a variable section for different forms of "deliverable".  This would initially be a digital signature which the user typed their name into, and would expand to photo/file upload.

## Testing
I haven't implemented it yet because I'm terrible!  Once I have each piece working such that shit can display, unit tests.  Unit tests for everyone.

## Future Features
There are two glaringly huge features I want to implement, which are by-laws and a reddit-style discussion system for motions.  They get their own sections.  Random things I want in here go in no particular order starting now:
- There should be mulitple ways to "deliver" a deliverable, ranging from writing some text, signing your virtual name, uploading a photo or file, etc.
- Once we have by-laws and motion discussion, we need to have Votes in the system.  You should get votes like people get notifications, telling you there's something to be decided on.
- Once the system supports actual interaction between these data elements, there should be a timeline view of groups which displays all recent actions to members.  It should integrate different permission levels so non-members can get a gloss of what's happening but current members can be an in-depth view on the goings on of the organization.
- Outline admin functionality.  What functions can only an admin perform, what functions can a member perform, how do we make those settings up to the user?  More importantly, how do I start integrating a full permissions sytem?
- A points logger.  All changes in points (namely when a responsibility becomes delivered and the member's point count increases) need to be logged in the system so the logs can be manually parsed just in case.  Each log should contain the responsibility delivered, the user who was awarded points, the timestamp at which it was delivered, the points awarded, the user's prior point count, and their subsequent point count.
- Thought on the points system -- the duration over which points accumulate needs to be a setting, so each group can determine when (or if) they refresh.
- A reminder system which lets users assigning tasks specify a time for email and text message reminders to the person who has to do the task.
- Group templates!  Users should be able to say whether they're making a club, fraternity, sports team, project group, company, etc.

### By-Laws by Wiki

### Motion Discuss by reddit
