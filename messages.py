#!/usr/bin/env python3

import slack
import os

def send_message(message):
    client = slack.WebClient(token=os.environ['SLACK_API_TOKEN'])
    response = client.chat_postMessage(channel='#python',text=message)




