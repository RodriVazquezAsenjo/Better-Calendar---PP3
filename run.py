import os.path
import pytz
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar"]
current_time = datetime.now(pytz.timezone('Europe/London'))
timezone = pytz.timezone('Europe/London')

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
        event_summary = input (('Please enter your event title (max 100 chars): \n'))
        if len(event_summary) == 0:
            raise ValueError ('Error: Title is required!\n')
        elif len(event_summary) > 100:
            print (f'Error: Title is too long! Maximum 100 characters, you entered: {len(event_summary)}\n')
        else: 
            print("Nice! Let's move to the next step\n")
            return event_summary   
        
def collect_event_priority ():
    while True:
        try:
            event_priority = int(input('Enter event priority (1-5):\n').strip())
            if 1 <= event_priority <= 5:
                return event_priority
            else:
                print('Error: Priority must be between 1 and 5.')
        except ValueError:
            print('Error: Invalid input, please enter an integer between 1 and 5.')

def collect_event_duration():
    while True:
        try:
            event_duration = input('Enter event duration (HH:MM):\n').strip()
            hours, minutes = map(int, event_duration.split(':'))
            return timedelta(hours=hours, minutes=minutes)
        except (ValueError, IndexError):
            print('Error: Invalid format. Please enter the duration in HH:MM format.')

def collect_event_deadline():
    while True:
        try:
            deadline_input = input('Enter deadline (dd/mm/yyyy HH:MM):\n').strip()
            event_deadline= timezone.localize(datetime.strptime(deadline_input, '%d/%m/%Y %H:%M'))
            return event_deadline if event_deadline > current_time else print('Error: The deadline must be a future date.')
        except ValueError:
            print('Error: Invalid format. Please enter the deadline in "dd/mm/yyyy HH:MM" format.')
            
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
    creds = authenticate_google_calendar()
    service = build("calendar", "v3", credentials=creds)
    time_min = new_event.start if use_start_time else current_time
    try:
        print("Getting the upcoming events")
        while new_event.deadline < time_min:
            new_event.deadline = (current_time + timedelta(days=1))
            print(f"Deadline is earlier than current time. Adjusting deadline to {new_event.deadline}")
        existing_events = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=time_min.isoformat(),
                timeMax = new_event.deadline.isoformat(),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = existing_events.get("items", [])
        if not events:
            print("No upcoming events found.")
            return []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"],'\n')
        return events 
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []
    
def start_time_formatting(x):
    minute_block = (x.minute // 15 +1) *15 
    result = x.replace(day = x.day + 1, hour = 0, minute = 0) if x.hour == 23 else x.replace(hour = x.hour + 1, minute = 0)
    return result if minute_block == 60 else x.replace(minute = minute_block)     
  
def allocate_event(new_event, events):
    new_event.start = start_time_formatting(current_time)
    event_scheduled = False
    for event in events:
        existing_event_start = datetime.strptime(event["start"].get("dateTime", event["start"].get("date")), '%Y-%m-%dT%H:%M:%S%z')
        existing_event_end = datetime.strptime(event["end"].get("dateTime", event["end"].get("date")), '%Y-%m-%dT%H:%M:%S%z')
        timedelta = existing_event_start - new_event.start
        print (f'Time difference between {new_event.start} and {existing_event_start} is {timedelta}')
        if timedelta >= new_event.duration:
            add_event(new_event)
            event_scheduled = True
            break
        else:
            start_time_formatting(existing_event_end)
            new_event.start = existing_event_end
            print(f"Event '{new_event.summary}' moved to {new_event.start}")
    if not event_scheduled:
        print('The event exceeds the deadline, your calendar will be readjusted')
        priority_assessment (new_event, events)
        event_scheduled = True
    return new_event    

def add_event(new_event):
    creds = authenticate_google_calendar()
    service = build("calendar", "v3", credentials=creds)
    new_event.end = new_event.start + new_event.duration
    if new_event.start is None or new_event.end is None:
        print('Error: Either the new event start or end time is set to None\n')
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
    events = get_existing_events(new_event, use_start_time=True)
    if not events:
        add_event(new_event)
        return
    for event in events:
        try:
            event_priority = description_breakdown(event.get('description'))
            event_priority_num = int(event_priority.get('Priority', 5))
            new_event_priority_num = int(new_event.priority)
            if event_priority_num > new_event_priority_num:
                print(f'Event {event["summary"]} has been reallocated due to lower priority.')
                add_event(new_event)
                retrieved_event = retrieve_event(event)
                service.events().delete(calendarId='primary', eventId=event['id']).execute()
                allocate_event(retrieved_event, events)
                return
            else:
                print(f"Event {event['summary']} has a higher or equal priority than the new event.")
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

def retrieve_event(event):
    creds = authenticate_google_calendar()
    service = build("calendar", "v3", credentials=creds)
    if event is None:
        print('Error: Event is None')
        return
    event = service.events().get(calendarId='primary', eventId=event['id']).execute()
    start = event["start"].get("dateTime", event["start"].get("date"))
    end = event["end"].get("dateTime", event["end"].get("date"))
    event_start = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S%z')
    event_end = datetime.strptime(end, '%Y-%m-%dT%H:%M:%S%z')
    event_priority = description_breakdown(event.get('description')).get('Priority', 5)
    event_duration = event_end - event_start
    event_deadline = event['description'].split('\n')[1].split(': ')[1]
    retrieved_event = Event(event['summary'], event_priority, event_duration, event_deadline)
    return retrieved_event

new_event = tool_start()
events = get_existing_events(new_event, use_start_time=False)
allocate_event (new_event, events)
