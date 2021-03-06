import os
import time
import re
import logging 
import inspect
import requests
import json
from requests.auth import HTTPBasicAuth

from slackclient import SlackClient

#print(inspect.getsource(logging))
logging.basicConfig(filname='example.log', filemode='w', level=logging.DEBUG)

s = requests.Session()
s.auth = ('acct:snackthenorth-stg@snackthenorthserviceuser', 'hackthenorth')

call_response = requests.get("https://gateway-staging.ncrcloud.com/", auth = ('acct:snackthenorth-stg@snackthenorthserviceuser', 'hackthenorth'))

# instantiate Slack client
slack_client = SlackClient('xoxb-436331105427-435861493473-IngPp06L9nVM6dzcU93g5Nit')
# snack_the_north's user ID in Slack: value is assigned after the bot starts up
snack_the_north_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "check for"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def find_value(id, json_repr):
    results = []

    def _decode_dict(a_dict):
        try: results.append(a_dict[id])
        except KeyError: pass
        return a_dict

    json.loads(json_repr, object_hook=_decode_dict)  # Return value ignored.
    return results

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == snack_the_north_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(EXAMPLE_COMMAND):
        #response = "Sure...write some more code then I can do that!"
        command1, command2, food, floor = command.split()
        
        find_value(food+floor, call_response)
        response = food + " is" + find_value + " there"
        
        #response = food + " is available on floor " + floor
        

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )



if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Snack the North connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        snack_the_north_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")



