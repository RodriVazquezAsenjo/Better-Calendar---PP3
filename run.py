# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high

import os.path
import pytz
from datetime import datetime, date, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

#Initial function to run when you open the program. It prompts you with an event you'd like to add. 
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
        self.start = None
        self.end = None

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
            hours, minutes = map(int, event_duration.split(':'))
            event_duration = timedelta(hours=hours, minutes=minutes)
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
    
    summary = collect_event_title()
    priority = collect_event_priority()
    duration = collect_event_duration()
    deadline = collect_event_deadline()
    new_event = Event(summary, priority, duration, deadline)
    print (f'Your new event is called {new_event.summary}, with a priority {new_event.priority}, with a duration of {new_event.duration} and a deadline for {new_event.deadline}')
    return new_event

def get_existing_events(new_event, use_start_time = False):
    new_event_deadline = new_event.deadline
    creds = authenticate_google_calendar()
    new_event_deadline = new_event_deadline.strftime('%Y-%m-%dT%H:%M:%S%z') + 'Z'
    try:
        service = build("calendar", "v3", credentials=creds)
        now = datetime.now(pytz.timezone("Europe/London")).isoformat()
        print("Getting the upcoming events")
        time_min = new_event.start if use_start_time else now
        if new_event_deadline < time_min:
            new_event_deadline = (pytz.timezone("Europe/London").localize(datetime.now() + timedelta(days=1))).isoformat()
        existing_events = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=time_min,
                timeMax = new_event_deadline,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = existing_events.get("items", [])

        if not events:
            print("No upcoming events found.")

        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])
            print('\n')  
        return events 

    except HttpError as error:
        print(f"An error occurred: {error}")
        return []

def start_time_formatting(x):
    minute_block = (x.minute // 15 +1) *15 
    if minute_block == 60:
        if x.hour == 23:
            return x.replace(day = x.day + 1, hour = 0, minute = 0)
        else:
            return x.replace(hour = x.hour + 1, minute = 0)
    else:
        return x.replace(minute = minute_block)
    
        
def allocate_event(new_event, events):
    current_time = datetime.now(pytz.timezone('Europe/London'))
    new_event.start = start_time_formatting(current_time)
    new_event.end = new_event.start + new_event.duration
    event_scheduled = False
    for event in events:
        existing_event_start = datetime.strptime(event["start"].get("dateTime", event["start"].get("date")), '%Y-%m-%dT%H:%M:%S%z')
        existing_event_end = datetime.strptime(event["end"].get("dateTime", event["end"].get("date")), '%Y-%m-%dT%H:%M:%S%z')
        timedelta = existing_event_start - new_event.start
        print (f'Time difference between {new_event.start} and {existing_event_start} is {timedelta}')
        print (type(timedelta))
        if timedelta >= new_event.duration:
            add_event(new_event)
            event_scheduled = True
            break
        else:
            start_time_formatting(existing_event_end)
            new_event.start = existing_event_end
            new_event.end = new_event.start + new_event.duration
            timedelta = existing_event_start - new_event.start
            print(f"Event '{new_event.summary}' moved to {new_event.start}")
    if not event_scheduled:
        print('The event exceeds the deadline, your calendar will be readjusted')
        priority_assessment (new_event, events)
        event_scheduled = True
    return new_event    
        

def add_event(new_event):
    creds = authenticate_google_calendar()
    service = build("calendar", "v3", credentials=creds)
    if new_event.start is None or new_event.end is None:
        print('Error: Either the new event start or end time is set to None\n')
        print (type(new_event.start))
        print (type(new_event.end))
        print (type(new_event.duration))
        return
    event = {
    'summary': new_event.summary,
    'description': f'Priority: {new_event.priority} \nDeadline: {new_event.deadline}',
    'start': {
        'dateTime': new_event.start.isoformat(),
        'timeZone': 'Europe/London',
    },
    'end': {
        'dateTime': new_event.end.isoformat(),
        'timeZone': 'Europe/London',
    }
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    print (f"Event created: {event.get('htmlLink')}\n")
    print (f'Your event {new_event.summary} has been added to your calendar from {new_event.start} to {new_event.end} \n')
    

def priority_assessment(new_event, events):
    creds = authenticate_google_calendar()
    service = build("calendar", "v3", credentials=creds)
    print('Assessing priority of existing events')
    print (new_event.start)
    events = get_existing_events(new_event, use_start_time=True)
    for event in events:
        try:
            event_priority = description_breakdown(event.get('description'))
            event_priority_num = int(event_priority.get('Priority', 5))
            new_event_priority_num = int(new_event.priority)
            if event_priority_num > new_event_priority_num:
                service.events().delete(calendarId='primary', eventId=event['id']).execute()
                print(f'Event {event["summary"]} has been deleted due to lower priority.')
                add_event(new_event)
            else:
                print(f"Event {event['summary']} has a higher or equal priority than the new event.")
                return
        except Exception as e:
            print(f"Error processing event {event['id']}: {str(e)}")
    
def description_breakdown(event):
    if event is None:
        return {'Priority': '5'}
    lines = event.splitlines()
    event_priority_dict = {}
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            event_priority_dict[key.strip()] = value.strip()
    return event_priority_dict

new_event = tool_start()
events = get_existing_events(new_event, use_start_time=False)
allocate_event (new_event, events)
