# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high


#importing the main function from quickstart to obtain the upcoming events
from quickstart import main
from datetime import datetime

#Initial function to run when you open the program. It prompts you with an event you'd like to add. 
    #Potentially it should just prompt you with the option to run?


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
    return event_priority 

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
            break
        except ValueError as e:
            print('The deadline should be in date, hours and minutes (day/month/year hours:minutes format), please try again!')
    print("Nice! Let's move to the next step\n")
    return event_deadline

def tool_start():
    print ("Hi! Let's get the first item of the event\n")
    collect_event_title()
    collect_event_priority()
    collect_event_duration()
    collect_event_deadline()

tool_start()