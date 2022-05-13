'implementation for other functions'
import re
from data_stores import channel_datastore, auth_datastore
#pylint: disable = C0301
from data_stores import reset_channels_datastore, reset_auth_datastore, reset_messages_datastore, reset_resetcode_datastore
from error import InputError, AccessError

def clear():
    'calling functions from data_stores file to clear the stores'
    reset_channels_datastore()
    reset_auth_datastore()
    reset_messages_datastore()
    reset_resetcode_datastore()

#pylint: disable = R0912
def admin_userpermission_change(token, u_id, permission_id):
    """this function will change a users permissions"""
    auth_store = auth_datastore()
    channel_store = channel_datastore()
    valid_uid = False
    valid_token = False
    for i in auth_store:
        if i['token'] == token and i['permission_id'] == 1:
            valid_token = True
        if i['u_id'] == u_id:
            valid_uid = True
            channel_owner = {
                'u_id': i['u_id'],
                'name_first': i['name_first'],
                'name_last': i['name_last'],
            }
    if not valid_token:
        raise AccessError(description="Not a valid admin")

    if not valid_uid:
        raise InputError(description="Not a valid uid")

    # Valid token
    if permission_id not in (1, 2):
        raise InputError(description="Not a valid permission id")

    if permission_id == 1:
        for i in auth_store:
            if i['u_id'] == u_id:
                i['permission_id'] = 1
        for chan in channel_store:
            for person in chan['members']:
                if person['u_id'] == u_id:#person is a member; move it to owner_list
                    chan['owners'].append(channel_owner)
                    chan['members'].remove(person)
    if permission_id == 2:
        for i in auth_store:
            if i['u_id'] == u_id:
                i['permission'] = 2
    #if the user' s permission id is 1, they become the owner of channel of they join.
    ##people with permission id 1, they can set other with permission id 1 to be 2
    return {}

def search(token, query_str):
    'implementation for search'
    auth_store = auth_datastore()
    channel_store = channel_datastore()

    messages = []

    for i in auth_store:
        if i['token'] == token:
            u_id = i['u_id']

    for chan in channel_store:
        for j in chan['members']:
            if j['u_id'] == u_id:
                for msg in chan['messages']:
                    if re.search(query_str.lower(), msg['message'].lower()):
                        result = {
                            'message_id': msg['message_id'],
                            'u_id': msg['u_id'],
                            'message': msg['message'],
                            'time_created': msg['time_created'],
                        }
                        messages.append(result)

        for j in chan['owners']:
            if j['u_id'] == u_id:
                for msg in chan['messages']:
                    if re.search(query_str.lower(), msg['message'].lower()):
                        result = {
                            'message_id': msg['message_id'],
                            'u_id': msg['u_id'],
                            'message': msg['message'],
                            'time_created': msg['time_created'],
                        }
                        messages.append(result)

    return messages


def users_all(token): #pylint: disable=W0613
    'implementation of the users all function'

    auth_store = auth_datastore()
    user_details = {}

    users = []

    if len(auth_store) == 0:
        return []


    for j in auth_store:
        user_details = {
            'u_id': j['u_id'],
            'email': j['email'],
            'name_first': j['name_first'],
            'name_last': j['name_last'],
            'handle_str': j['handle_str']

        }
        users.append(user_details)

    return users
