# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high


#importing the main function from quickstart to obtain the upcoming events
from quickstart import main

#Initial function to run when you open the program. It prompts you with an event you'd like to add. 
    #Potentially it should just prompt you with the option to run?


def collect_event_title ():
    while True:
        event_summary = input (('Welcome! Please enter your event below: \n'))
        if event_summary == '':
            print ('You need to add a title!\n')
        elif len(event_summary) >= 10:
            print (f'Too long! Maximum 10 characters, you typed {len(event_summary)} characters\n')
        else: break
        
def tool_start():
    collect_event_title()

tool_start()