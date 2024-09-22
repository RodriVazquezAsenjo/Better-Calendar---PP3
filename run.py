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
        self.added = False


# original code amended from https://developers.google.com/calendar/quickstart/python
def authenticate_google_calendar():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'path_to_your_credentials.json', scopes=[
                'https://www.googleapis.com/auth/calendar'])
            creds = flow.run_console()  # Use run_console instead of run_local_server
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

# original code amended from https://developers.google.com/calendar/quickstart/python
def authenticate_and_build_service():
    """
    Handles Google Calendar authentication and returns the service object.
    """
    creds = authenticate_google_calendar()
    service = build("calendar", "v3", credentials=creds)
    return creds, service


def collect_event_title():
    """
    Function to collect the event title from the user.
    The function will raise an error if the title is
    empty or longer than 100 characters.
    """
    while True:
        event_summary = input(('Enter your event title (max 100 chars): \n'))
        if len(event_summary) == 0:
            raise ValueError('Error: Title is required!\n')
        elif len(event_summary) > 100:
            print(f'Error: Title is too long! Maximum 100 characters, '
                  f'you entered: {len(event_summary)}\n')
        else:
            print("Nice! Let's move to the next step\n")
            return event_summary


def collect_event_priority():
    """
    Function to collect the event priority from the user.
    The function will raise an error if the priority is
    not an integer between 1 and 5."""
    while True:
        try:
            event_priority = int(input('Enter event priority '
                                       '(1-5):\n').strip())
            if 1 <= event_priority <= 5:
                return event_priority
            else:
                print('Error: Priority must be between 1 and 5.')
        except ValueError:
            print('Error: Invalid input, please '
                  'enter an integer between 1 and 5.')


def collect_event_duration():
    """
    Function to collect the event duration from the user.
    The function will raise an error if the duration is
    not in the HH:MM format.
    """
    while True:
        try:
            event_duration = input('Enter event duration (HH:MM):\n').strip()
            hours, minutes = map(int, event_duration.split(':'))
            return timedelta(hours=hours, minutes=minutes)
        except (ValueError, IndexError):
            print('Error: Invalid format. Please enter '
                  'the duration in HH:MM format.')


def collect_event_deadline():
    """
    Function to collect the event deadline from the user.
    The function will raise an error if the deadline is
    not in the dd/mm/yyyy HH:MM format.
    """
    while True:
        try:
            deadline_input = input('Enter deadline '
                                   '(dd/mm/yyyy HH:MM):\n').strip()
            event_deadline = timezone.localize(
                datetime.strptime(deadline_input, '%d/%m/%Y %H:%M'))
            return event_deadline if event_deadline > current_time else print(
                'Error: The deadline must be a future date.')
        except ValueError:
            print('Error: Invalid format. Please enter the '
                  'deadline in "dd/mm/yyyy HH:MM" format.')


def tool_start():
    """
    Function to start the tool and collect the event details.
    The function will call the collect_event_title,
    collect_event_priority, collect_event_duration,
    and collect_event_deadline functions to get the
    event details from the user.
    """
    print("Hi! Let's get the first item of the event\n")
    summary = collect_event_title()
    priority = collect_event_priority()
    duration = collect_event_duration()
    deadline = collect_event_deadline()
    new_event = Event(summary, priority, duration, deadline)
    print(f'Your new event is called {new_event.summary}, with a '
          f'priority {new_event.priority}, with a duration of '
          f'{new_event.duration} and a deadline for {new_event.deadline}')
    return new_event

 
# original code amended from https://developers.google.com/calendar/quickstart/python
def get_existing_events(new_event, use_start_time=False):
    """
    Function to get the upcoming events from the user's calendar.
    The function will return the events that are scheduled
    between the current time and the deadline of the new event.
    """
    creds = authenticate_google_calendar()
    service = build("calendar", "v3", credentials=creds)
    time_min = new_event.start if use_start_time else current_time
    try:
        print("Getting the upcoming events")
        while new_event.deadline < time_min:
            new_event.deadline = (current_time + timedelta(days=1))
            print(f'Deadline is earlier than current time. '
                  f'Adjusting deadline to {new_event.deadline}')
        existing_events = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=time_min.isoformat(),
                timeMax=new_event.deadline.isoformat(),
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
            print(start, event["summary"], '\n')
        return events
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []


def start_time_formatting(x):
    """
    Function to format the start time of the event.
    The function will round the start time to the nearest
    15-minute block and return the updated time.
    """
    minute_block = (x.minute // 15 + 1) * 15
    if x.hour == 23:
        result = x.replace(day=x.day + 1, hour=0, minute=0)
    else:
        result = x.replace(hour=x.hour + 1, minute=0)

    if minute_block == 60:
        return result
    else:
        return x.replace(minute=minute_block)


def allocate_event(new_event):
    """
    Function to allocate the new event to the user's calendar.
    The function will call the get_existing_events function
    to get the upcoming events from the user's calendar.
    The function will then check if the new event can be
    scheduled between the existing events. If the event
    can't be scheduled, the function will call the
    priority_assessment function to check if the new event
    has a higher priority than the existing events.
    """
    events = get_existing_events(new_event, use_start_time=False)
    new_event.start = start_time_formatting(current_time)
    for event in events:
        existing_event_start = datetime.strptime(
            event["start"].get("dateTime", event["start"].get(
                "date")), '%Y-%m-%dT%H:%M:%S%z')
        existing_event_end = datetime.strptime(
            event["end"].get("dateTime", event["end"].get(
                "date")), '%Y-%m-%dT%H:%M:%S%z')
        timedelta = existing_event_start - new_event.start
        print(f'Time difference between {new_event.start} and'
              f' {existing_event_start} is {timedelta}')
        if timedelta >= new_event.duration:
            add_event(new_event)
            new_event.added = True
            break
        else:
            start_time_formatting(existing_event_end)
            new_event.start = existing_event_end
            print(f"Event '{new_event.summary}' moved to {new_event.start}")
    if not new_event.added:
        if new_event.start > new_event.deadline:
            print('The event exceeds the deadline, '
                'your calendar will be readjusted')
            priority_assessment(new_event, events)
        else:
            add_event(new_event)
            new_event.added = True
            return
            
    return new_event

# original code amended from https://developers.google.com/calendar/quickstart/python
def add_event(new_event):
    """
    Function to add the new event to the user's calendar.
    The function will call the authenticate_google_calendar
    function to authenticate the user's calendar.
    The function will then create the event dictionary
    and add the event to the user's calendar.
    """
    creds = authenticate_google_calendar()
    service = build("calendar", "v3", credentials=creds)
    new_event.end = new_event.start + new_event.duration
    if new_event.start is None or new_event.end is None:
        print('Error: Either the new event start or end time is set to None\n')
        return
    event = {
        'summary': new_event.summary,
        'description': f'Priority: {new_event.priority} \n'
                       f'Deadline: {new_event.deadline}',
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
    print(f"Event created: {event.get('htmlLink')}\n")
    print(f'{new_event.summary} has been added '
          f'to your calendar from {new_event.start} to {new_event.end} \n')


def priority_assessment(new_event, events):
    """
    Function to assess the priority of the new event.
    The function will call the get_existing_events function
    to get the upcoming events from the user's calendar.
    The function will then check if the new event has a
    higher priority than the existing events. If the new
    event has a higher priority, the function will call
    the add_event function to add the new event to the
    user's calendar. If the new event has a lower priority,
    the function will call the add_event function to add
    the new event to the user's calendar and remove the
    existing event with the lower priority.
    """
    creds = authenticate_google_calendar()
    service = build("calendar", "v3", credentials=creds)
    print('Assessing priority of existing events')
    events = get_existing_events(new_event, use_start_time=False)
    new_event.start = start_time_formatting(current_time)
    for event in events:
        try:
            if not new_event.added:
                existing_event = obtain_current_event_info(event)
                if int(existing_event.priority) > int(new_event.priority):
                    print(f'Event {event["summary"]} has lower priority.')
                    # original code amended from 
                    # https://developers.google.com/calendar/quickstart/python
                    service.events().delete(calendarId='primary',
                                            eventId=event['id']).execute()
                    add_event(new_event)
                    new_event.added = True
                    print(f"Event '{event['summary']}' has been "
                          " removed from your calendar.")
                    reschedule_event(existing_event)
                    break
                else:
                    start_time_formatting(existing_event.end)
                    new_event.start = existing_event.end
                    print(f"Event {event['summary']} has a higher "
                          f"or equal priority than the new event."
                          f"{new_event.summary} has been moved to {new_event.start}")
                    if new_event.start > new_event.deadline:
                        deadline_extension(new_event)
        except Exception as e:
            print(f"Error processing event {event['id']}: {str(e)}")
    if not new_event.added:
        print('No more future events found in your calendar')
        add_event(new_event)
        new_event.added = True
        return
        

def obtain_current_event_info(event):
    """
    Function to obtain the information of the current event.
    The function will get the start and end time of the
    existing event and calculate the duration of the event.
    The function will then call the description_breakdown
    function to break down the event description and get
    the priority of the event.
    """
    existing_event_end = datetime.strptime(event["end"].get(
        "dateTime", event["end"].get("date")), '%Y-%m-%dT%H:%M:%S%z')
    event_start = datetime.strptime(event["start"].get(
        "dateTime", event["start"].get("date")), '%Y-%m-%dT%H:%M:%S%z')
    event_duration = existing_event_end - event_start
    event_priority = description_breakdown(event.get('description', ''))
    event_priority_num = int(event_priority.get('Priority', 5))
    description_lines = event.get('description', '').split('\n')
    if len(description_lines) > 1 and 'Deadline' in description_lines[1]:
        try:
            event_deadline = description_lines[1].split(': ')[1]
        except IndexError:
            print('Error: Invalid format for'
                  ' deadline in the event description.')
            event_deadline = collect_event_deadline()
    else:
        event_deadline = collect_event_deadline()
    existing_event = Event(event['summary'], event_priority_num,
                           event_duration, event_deadline)
    existing_event.start = event_start
    existing_event.end = existing_event_end
    print(f'Existing Event: {existing_event.summary}, '
          f'Priority: {existing_event.priority}, '
          f'Duration: {existing_event.duration}, '
          f'Deadline: {existing_event.deadline}')
    return existing_event


def deadline_extension(new_event):
    """
    Function to extend the deadline of the new event.
    The function will ask the user if they want to extend
    the deadline of the new event. If the user wants to
    extend the deadline, the function will call the
    collect_event_deadline function to get the new deadline
    from the user. The function will then call the
    allocate_event function to allocate the new event.
    """
    user_input = input('Would you like to extend '
                        'the deadline? Enter y/n: \n')
    if user_input == 'y':
        new_deadline = collect_event_deadline()
        new_event.deadline = new_deadline
        print(f"New deadline for '{new_event.summary}' "
                f"is {new_event.deadline}")
        allocate_event(new_event)
    else:
        print("The event won't be added to your calendar")
        return


def description_breakdown(event):
    """
    Function to break down the event description.
    The function will split the event description into
    lines and create a dictionary with the key-value pairs.
    """
    if event is None:
        return {'Priority': '5'}
    lines = event.splitlines()
    event_priority_dict = {}
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            event_priority_dict[key.strip()] = value.strip()
    return event_priority_dict


def main():
    """
    Function to start the tool and allocate the new event.
    The function will call the tool_start function to get
    the event details from the user. The function will then
    call the allocate_event function to allocate the new
    event to the user's calendar.
    """
    new_event = tool_start()
    allocate_event(new_event)


def reschedule_event(existing_event):
    """
    Function to reschedule the existing event.
    The function will ask the user if they want to
    reschedule the existing event. If the user wants
    to reschedule the event, the function will call the
    main function to start the tool again. If the user
    doesn't want to reschedule the event, the function
    will print a message that the event has been removed.
    """
    print(f'The details were: \n'
          f'Summary: {existing_event.summary} \n'
          f'Priority: {existing_event.priority} \n'
          f'Duration: {existing_event.duration} \n'
          f'Deadline: {existing_event.deadline} \n'
          f'Do you want to reschedule the event?')
    reschedule = input('Enter y/n: \n')
    if reschedule == 'y':
        main()
    else:
        print('The event has been removed from your calendar. \n')
        return


new_event = None

if __name__ == "__main__":
    main()