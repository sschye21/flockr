'this file is the implementation of the channe;s functions'
from error import InputError
from data_stores import channel_datastore, auth_datastore

# CHANNELS_CREATE
# Creates a new channel with that name that iether a public or private channel.
def channels_create(token, name, is_public):
    'implementation of the channels create function'
    channel_store = channel_datastore()
    channel_owner = {}
    new_channel_details = {}

    auth_store = auth_datastore()
    token_valid = False
    for i in auth_store:
        if i['token'] == token:
            token_valid = True
            user = i #user = i because you wanna user has many properties not just token
            channel_owner = {
                'u_id': user['u_id'],
                'name_first': user['name_first'],
                'name_last': user['name_last'],

            }

    if not token_valid:
        raise InputError(description="The token is not found")

    if len(name) < 21:
        if is_public is True:
            new_channel_details = {
                'channel_id': int(len(channel_store)+1),
                'name':  name,
                'is_public': True,
                'members':[],
                'owners':[],
                'messages': [],
                'is_active':False,
                'standup':[],
                'time_finish':None,
                'schedule':[],
            }
        else:
            new_channel_details = {
                'channel_id': int(len(channel_store)+1),
                'name':  name,
                'is_public': False,
                'members':[],
                'owners':[],
                'messages': [],
                'is_active':False,
                'standup':[],
                'time_finish':None,
                'schedule':[],
            }
    else:
        raise InputError(Exception)

    new_channel_details['owners'].append(channel_owner)

    channel_store.append(new_channel_details)
    return new_channel_details['channel_id']

# CHANNELS_LIST
# Provides a list of channels (and associated details that authorised user
# is part of).
def channels_list(token):
    """implementation of the channels list function"""
    channel_store = channel_datastore()
    auth_store = auth_datastore()
    user_channels = []
    for i in auth_store:
        if i['token'] == token:
            u_id = i['u_id']
    for chan in channel_store:
        for j in chan['members']:
            if j['u_id'] == u_id:
                channel_details = {
                    'channel_id': chan['channel_id'],
                    'name': chan['name'],
                }
                user_channels.append(channel_details)
    for chan in channel_store:
        for j in chan['owners']:
            if j['u_id'] == u_id:
                channel_details = {
                    'channel_id': chan['channel_id'],
                    'name': chan['name'],
                }
                user_channels.append(channel_details)


    return user_channels

# CHANNELS_LISTALL
# Provides a list of all channels (and their associated details).
def channels_listall(token): #pylint: disable=C0103
    'implementation of the channels listall function'

    channel_store = channel_datastore()
    auth_store = auth_datastore()

    channel_details = {}
    channels = []

    if len(channel_store) == 0:
        return channels

    for i in auth_store:
        if i['token'] == token:
            for chan in channel_store:
                channel_details = {
                    'channel_id': chan['channel_id'],
                    'name': chan['name'],
                }
                channels.append(channel_details)

    return channels
