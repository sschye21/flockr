import json
import threading

channels_data = []
messages_data = []
auth_data = []

def channel_datastore():
    global channels_data
    if len(channels_data) == 0:
        try:
            with open('channel_data_store.json', 'r') as FILE:
                channels_data = json.load(FILE)
        except:
            pass
    return channels_data

def auth_datastore():
    global auth_data
    if len(auth_data) == 0:
        try:
            with open('channel_data_store.json', 'r') as FILE:
                auth_data = json.load(FILE)
        except:
            pass
    return auth_data

def messages_datastore():
    global messages_data
    return messages_data


def reset_channels_datastore():
    global channels_data
    channels_data = []
    return

def reset_auth_datastore():
    global auth_data
    auth_data = []
    return

def reset_messages_datastore():
    global messages_data
    messages_data = []
    return


