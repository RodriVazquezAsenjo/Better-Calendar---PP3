# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high

import os.path
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

#Initial function to run when you open the program. It prompts you with an event you'd like to add. 
    #Potentially it should just prompt you with the option to run?
#code originally obtained from Google Workspace Google Calendar API. Modified to suit. 
# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]



#Convert collected data to an instance of a class
class Event:
    def __init__(self, summary, priority, duration, deadline):
        self.summary = summary
        self.priority = priority
        self.duration = duration
        self.deadline = deadline

def authenticate_google_calendar():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    
    return creds

def collect_event_title ():
    while True:
        event_summary = input (('Please enter your event below: \n'))
        if event_summary == '':
            raise ValueError ('You need to add a title!\n')
        elif len(event_summary) > 100:
            raise ValueError (f'Too long! Maximum 100 characters, you typed {len(event_summary)} characters\n')
        else: break
    print("Nice! Let's move to the next step\n")
    return event_summary    

def collect_event_priority ():
    while True:
        print ("Event pririoties are ranked from 1 to 5, 1 being lowest priority and 5 the highest.\n")
        event_priority = input (('Enter your event priority here: \n'))
        if event_priority == '':
            raise ValueError ('Whoops! You need to enter a priority.\n')
        try:
            if int(event_priority)>= 1 or int(event_priority)<= 5:
                break
        except ValueError as e:
            print(f'Watchout! You entered {event_priority}, it should be between 1 and 5')
    print("Nice! Let's move to the next step\n")
    return int(event_priority) 

def collect_event_duration():
    while True:
        event_duration = input('Using a hours:minutes format, how long will the event last: \n')
        if event_duration == '':
            raise ValueError("Oh no! Seems like you didn't enter a duration, try again!.\n")
        try:
            event_duration = datetime.strptime(event_duration, '%H:%M')
            break
        except ValueError as e:
            print('The duration should be in hours and minutes (hours:minutes format), please try again!')
    print("Nice! Let's move to the next step\n")
    return event_duration

def collect_event_deadline():
    while True:
        event_deadline = input('Using a day/month/year hours/min format, when is the deadline for this project? \n')
        if event_deadline == '':
            raise ValueError("Oh no! Seems like you didn't enter a deadline, try again!.\n")
        try:
            event_deadline = datetime.strptime(event_deadline, '%d/%m/%Y %H:%M')
            if event_deadline > datetime.now():
                break
        except ValueError as e:
            print('The deadline should be a future date,in the follwoing format (day/month/year hours:minutes), please try again! Error: {e}')
    print("Nice! Let's move to the next step\n")
    return event_deadline

def tool_start():
    print ("Hi! Let's get the first item of the event\n")
    event_summary = collect_event_title()
    event_priority = collect_event_priority()
    event_duration = collect_event_duration()
    event_deadline = collect_event_deadline()
    new_event = Event(event_summary, event_priority, event_duration, event_deadline)
    print (f'Your new event is called {event_summary}, with a priority {event_priority}, with a duration of {event_duration} and a deadline for {event_deadline}')
    return new_event

def get_existing_events(event_deadline):
    creds = authenticate_google_calendar()
    event_deadline = event_deadline.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
    try:
        service = build("calendar", "v3", credentials=creds)
        now = datetime.now().isoformat() + "Z"  # 'Z' indicates UTC time
        print("Getting the upcoming 10 events")
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                timeMax = event_deadline,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return

        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])

        return events_result
        
        

    except HttpError as error:
        print(f"An error occurred: {error}")

def allocate_event(new_event, events_result):
    events = events_result.get('items', [])
    new_event.start = datetime.now().isoformat() + "Z"  # 'Z' indicates UTC time
    event_start = events_result["start"].get("dateTime", event["start"].get("date"))
    event_end = events_result["end"].get("dateTime", event["end"].get("date"))
    for event in events:
        time_delta = event_start - new_event.start
        try: 
            if time_delta < new_event.duration:
                new_event.start = event_end
            else:
                add_event()
                break
        except ValueError as e:
            print('There are no available spaces before your deadline.')
    return new_event.start

        

def add_event(new_event):
    creds = authenticate_google_calendar()
    service = build("calendar", "v3", credentials=creds)
    new_event.end = new_event.start + new_event.duration
    print(new_event.start)
    event = {
    'summary': new_event.summary,
    'start': {
        'dateTime': new_event.start,
        #'timeZone': '',
    },
    'end': {
        'dateTime': new_event.end,
        #'timeZone': '',
    },
    #'colorId': '',
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    print (f"Event created: {event.get('htmlLink')}")
    print ('new_event.end')

an_existing_event = get_existing_events(collect_event_deadline())
allocate_event(tool_start(), an_existing_event)
