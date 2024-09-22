# Project 3 - Better Calendar
[View the live project here](https://better-calendar-1ab256c687f2.herokuapp.com/)

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [User Stories](#user-stories)
- [Flow Chart](#flow-chart)
- [Data Model](#data-model)
- [Future Additions](#future-additions)
- [Technologies Used](#technologies-used)
- [Testing](#testing)
- [Known Bugs](#known-bugs)
- [Deployment](#deployment)
- [Acknowledgments](#acknowledgements)

## Introduction

Better Calendar is a Command Line Interface tool which allows you to add events
to your calendar while not having to worry about when to fit an event in!

The goal of this tool is to minimize as much as feasible the input from the user.
The app is an optimizer, to remove time-spending activities such as sorting out 
your schedule. 

The tool will automatically identify spots where you can fit in your event based
on calendar availability and priorities.

This tool is aimed for everyone and anyone who wants to optimize their scheduling
processes, and subject to further development, could even sort out events, meetings,
calls or appointments between a multitude of people!

## Features

### Feature 1
The very first feature of the tool is the run event. When the program is run a
series of prompts are raised in the command interface. 

The first prompt is the event title collection. The user can input any string, however,
should the user return the input blank or larger than 100 characters, an error message
is raised and the user is prompted to add the title again. 

The second prompt is the event priority collection. The user will rank the event in 
priority from 1 to 5, 1 being the highest priority and 5 the lowest. If the value
returned is not an integer, the user is prompted to add the priority again.

The third prompt is the event duration collection. The user will add the time duration
of the event in hours:minute format. If the input is in the incorrect format, the user
is promted to add the duration again.

The fourth prompt is the event deadline duration. The user will add the deadline of the
event in the format of dd/mm/yyyy hh:mm. If the user input is in the incorrect format,
the user is prompted to add the duration again. 

### Feature 2

Google calendar's API is called to obtained all the events up to the event deadline provided.
The events are then returned in Date : Title format. 

### Feature 3

The tool then aims to add the new event. It will do this by first looping through each of the 
events. If the events are exhausted and the event will compare priorities with each of the events. 
If the priorities are equal or higher and the event runs out of available time before the deadline,
a message is returned stating that no available time was found before the deadline. If the event
has a higher priority than the looped existing events, they will be added and the existing event
removed. 

### Feature 4

The tool will ask for a deadline extension for the proposed event if no available time is found. It 
then looks for a spot with the updated deadline. This process loops until an available spot is found. 

### Feature 5 

The tool will ask the user if they want to reschedule the deleted event. If yes, the user will
re-input the details of the rescheduled event, and it will loop through the same process as the new
event. 

## User Stories

- As a busy professional, I want a calendar optimizer to prioritize and schedule my tasks based on
  deadlines and importance, so I can maximize productivity without feeling overwhelmed.

- As a student, I want a calendar optimizer that helps me balance my study sessions, assignments,
  and personal time, so I can manage my workload more efficiently and reduce stress before exams.

- As a freelancer, I want a calendar optimizer to allocate time for client projects and personal
  tasks, ensuring I meet deadlines without overbooking myself.

- As a project manager, I want a calendar optimizer that can distribute tasks across my team’s
  calendars, ensuring that deadlines are met and workload is evenly balanced among team members.

All of these user stories have been AI generated to understand the concerns that different users 
might have regarding their calendars. It is understood that all of these are met by this project proposal. 

## Flowchart

## Data Model

Input is received from the user. Data is retrieved from the Google Calendar API, analysed based on their
duration, decription, start and end dates and then the algorithm works out an available spot for the
proposed event, including potential rescheduling of the exisitng events. 
## Future Additions

### Future Addition 1
Additional formats in which the data can be input into the system.
Automated rescheduling of the existing events.
Confirmation of desired input in the collection methods. 
Set timetables - Add between what time to what time you wish to have your event added. 
Add a desired target schedule for your added event. 

## Technologies and tools used

- Language: Python 3.12.1 (https://www.python.org/downloads/)
- Version Control: [Git](https://git-scm.com/)
- Public repository: [GitHub](https://github.com/)
- Deployment: [Heroku](https://dashboard.heroku.com/)
- Google Calendar API: [Google Calendar API](https://developers.google.com/calendar/api/guides/overview)
- DateTime 5.5 library python: [DateTime](https://pypi.org/project/DateTime/)
- Pycodestyle 2.12.1, formerly known as PEP8: [Pycodestyle]([https://pycodestyle.pycqa.org/en/latest/](https://pypi.org/project/pycodestyle/)

## Testing

Testing has been done in the following methods:

### Pycodestyle / PEP 8

The downloadable tool was installed in Python, ran and all outstanding elements which required fixing
were fixed. 

### Functionality testing:

| Task Name                       | Task Action                       | Expected Action                                                                         |Result|
|---------------------------------|-----------------------------------|-----------------------------------------------------------------------------------------|------|
| Data Collection                 | Input unexpected data in feature 1| Error Message triggered                                                                 | Pass |
| Retrieve existing events        | Automatic process                 | Existing events between now and deadline listed                                         | Pass |
| Event iteration                 | Automatic process                 |new event updates start time if no available space through loop                          | Pass |
| Event added                     | Automatic process                 | If available space before deadline, event should appear in google calendar              | Pass |
|Prompted to extend deadline      | Automatic process                 | if no available spot, prompt appears                                                    | Pass |
|Event added for higher priorities| Automatic process                 |Existing event deleted, new event added, prompt asks to reschedule existing event deleted| Pass |
|Event rescheduled                |Input 'y' to prompt                | event appears in the calendar rescheduled                                               | Pass |



## Known Bugs
### Bug 1
When a high-priority event replaces a lower-priority event, there's a possibility that the high-priority
event may extend and overlap with the subsequent event, as the following event is not automatically 
removed or adjusted. This overlapping issue needs further debugging and development to ensure that calendar
events are managed properly.

To handle this, the following steps could be incorporated:

#### Gap Calculation: 
After the high-priority event replaces the lower-priority one, calculate the time gap between the end of the
high-priority event and the start of the next scheduled event. If the gap is insufficient, push the next event
to a later time slot.

#### Conflict Resolution:
If rescheduling the high-priority event still causes conflicts with the following event, the system should 
either reschedule the next event based on its priority or offer alternative solutions (e.g., move it to the 
next available time slot).

#### User Prompts for Edge Cases:
In cases where no automatic adjustment can resolve the conflict, prompt the user for a decision—whether they 
want to keep the high-priority event or allow the next event to proceed as planned.

This can be done by updating the timeMin variable of get_existing_events() to the new_event.start and checking
if the new_event.end is later than a existing_event.start. If so either the following event is pushed back or
the new_event is not added.

Due to time constraints this feature has not been added. 

## Deployment

First, update the requirements.txt file to include all necessary project dependencies. Follow these steps:

Open a terminal and run: pip3 freeze > requirements.txt
Commit the updated requirements.txt file to your GitHub repository and push the changes.
Log in to Heroku, or create a new account if you don’t have one already.

In the Heroku dashboard, click on Create New App. For new users, you’ll see a button right on the screen; for
existing users, you can find the option under the New dropdown at the top-right corner.

On the Create New App page, choose a unique name for your application, select the region, and click Create app.

Once your app is created, you’ll land on the app’s configuration page. You’ll need to configure settings on the 
Settings and Deploy tabs.

Setting Environment Variables:

Go to the Settings tab, scroll down to the Config Vars section, and click Reveal Config Vars.
In the key field, enter 'CREDS', and in the value field, paste the content of your creds.json file (which contains
your credentials for accessing the Google API). Then, click Add. Instructions for generating the creds.json file 
are available in the Google API and Spreadsheet Setup section above.

Configuring Buildpacks:

Still in the Settings tab, scroll down to the Buildpacks section.
Click Add buildpack, select Python, and save the changes.
Add another buildpack, select Node.js, and save the changes again. Make sure Python is listed first, followed 
by Node.js.

Linking with GitHub for Deployment:

Go to the Deploy tab in your app’s configuration page.
Under Deployment Method, select GitHub. If prompted, confirm the connection to your GitHub account.
Search for your GitHub repository and click Connect to 
link your Heroku app with your repository. Choose whether to enable Automatic Deploys, which will deploy the app 
whenever you push changes to the repository, or deploy manually by clicking Deploy Branch.

Running the App:

After the deployment completes, you can run the app by clicking the Open App button on the Heroku dashboard.

## Acknowledgments
Thank you to my mentor Brian Maccharia, who gave me valuable insights and discussions. 
