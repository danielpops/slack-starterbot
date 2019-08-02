import os
import time
import re
from slackclient import SlackClient


# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def parse_event(slack_event):
    """
        Parses a list of events coming from the Slack RTM API
    """
    if event["type"] == "message" and not "subtype" in event and not "bot_id" in event:
        user_id, message = parse_direct_mention(event["text"])
        event["is_direct"] = False
        event["mentioned_user"] = None
        if user_id == starterbot_id:
            event["is_direct"] = True
            event["mentioned_user"] = user_id
            event["text"] = message

        print event
        return event
    elif event["type"] == "reaction_added":
        pass
    elif event["type"] == "reaction_removed":
        pass

    return None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_event(event):
    """
        Executes bot command if the command is known
    """
    # Default to no response
    response = None
    
    if event["is_direct"]:
        if event["text"].startswith("hi"):
            response = "hi :wave:"
            slack_client.api_call(
                "reactions.add",
                channel=event["channel"],
                name="wave",
                timestamp=event["event_ts"],
            )
    else:
        # Do something else
        if "love" in event["text"]:
            slack_client.api_call(
                "reactions.add",
                channel=event["channel"],
                name="heart",
                timestamp=event["event_ts"],
            )

    if response:
        # Sends the response back to the channel
        slack_client.api_call(
            "chat.postMessage",
            as_user=True,
            channel=event["channel"],
            text=response
        )

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            parsed_event = None
            for event in slack_client.rtm_read():
                parsed_event = parse_event(event)
            if parsed_event:
                handle_event(parsed_event)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
