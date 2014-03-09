# Welcome
This is Groupify, a cloud-based group management platform.  In a sentence, it lets people make *groups* which have *members* who perform *roles* which have and distributed *responsibilities*.  Those responsibilities can optionally be worth points.  Groups can also connect to other groups in a hierarchy (i.e. a fraternity is a child of its national organization) or in partnership (i.e. a fraternity works with its school's IntraFraternity Council).  Documentation will be updated as the project continues!

## Current/Next Work
I need to figure out what front-end pages are required to make this thing work.  For the basest functionality, you need to be able to make an account, create a group, join/leave a group.  Create roles, assign them to members, take them away, change who it's assigned to.  Create responsibilities in a template fashion, give roles the ability to give them out, have them be doable and reward members with points.  Speaking of points, I need to make a points logger -- it just needs to sit on the database class and record every transaction based on the group.  Actually, based on everything.  We should be able to pick apart that points log however we want, to allow for many different views from different privacy levels.

If I have all of that in there, though, I think I could make a sample group.  The concept of responsibilities as a template is important.  It makes a responsibility a standard type of thing you have to get done.

## Database Schema
The system recognizes five underlying objects which correspond to database tables:
- Users
- Groups
- Memberships
- Roles
- Responsibilities

### Users
Users separated from the specific activity of each group.  All association is handled through memberships, allowing users to fluidly be a part of multiple groups.  It has the colums:
- Name (String)
- Email (Validated String)
- Phone Number (Optional)
- Bio (String)
- Memberships (Many to Many)
- Photo (Binary)

### Groups
Groups are collections of members.  They also hold roles.  Eventually, a group will exist with surrounding features like by-laws, motions for updates, and a discussion system.  For now, however, it is expressed as a collection of people.  It has the columns:
- Name (String)
- Members (One to Many)
- By-Line (String)
- Description (Long String)
- Roles (One to Many)
- Responsibilities (One to Many)

### Memberships
A membership contains all the information a user would want to interact with in the group.  Specifically, members perform roles, have responsibilities, and gather points.  It has the columns:
- Preferred Name (Optional String)
- Role (Many to Many)
- Given Responsibilities (Many to Many)
- Giving Responsibilities (Many to Many)
- Points (Integer)

### Roles
A role is part of a group, has a description, comes with some responsibilities, and also gives people the power to assign some types of responsibilities.  It also comes with a title, because of course.  The columns are:
- Name (Required String)
- Group (Foreign Key)
- Description (Long String)
- Giving Responsibilities (Many to Many)
- Given Responsibilities (Many to Many)

### Responsibilities
Lastly, a responsibility is the basic unit of getting things done.  It has a name, a description, a delivered Boolean, an optional points reward, and an additional comments section.  To stay true to form, the columns are:
- Name (Short String)
- Description (Medium String)
- Delivered (Boolean)
- Points (Integer)
- Comments (Short String)

## Front-End Functionality

## Future Features
There are two glaringly huge features I want to implement, which are by-laws and a reddit-style discussion system for motions.  They get their own sections.  Random things I want in here go in no particular order starting now:
- There should be mulitple ways to "deliver" a deliverable, ranging from writing some text, signing your virtual name, uploading a photo or file, etc.
- Once we have by-laws and motion discussion, we need to have Votes in the system.  You should get votes like people get notifications, telling you there's something to be decided on.

### By-Laws by Wiki

### Motion Discuss by reddit
