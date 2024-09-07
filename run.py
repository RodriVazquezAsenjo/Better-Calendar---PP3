# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high


#importing the main function from quickstart to obtain the upcoming events
from quickstart import main

#Initial function to run when you open the program. It prompts you with an event you'd like to add. 
    #Potentially it should just prompt you with the option to run?
def tool_start():
    event_summary = input ('Welcome! Please enter your event below: \n')
    #if event is validated
    event_priority = input("Choose a event priority: \n")
    #if event is validated
    event_length = input('How long will it take: \n')
    #if event is validated
    event_deadline = input ('Choose the deadline of the event: \n')
    return event_summary
tool_start()