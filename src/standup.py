'''stand up functions  implementations'''
from datetime import datetime, timezone
import threading
from error import InputError, AccessError
from data_stores import auth_datastore, channel_datastore
from channel import token_to_u_id
def check_inside_channel(token, channel_id):
    """check if user is inside channel"""
    auth_data = auth_datastore()
    channel_data = channel_datastore()
    valid_user = False
    for user in auth_data:
        if user['token'] == token:
            valid_user = True
    u_id = token_to_u_id(token)
    valid_token = False
    valid_channel = False
    for channel in channel_data:
        if channel['channel_id'] == channel_id:
            valid_channel = True
            for person in channel['members']:
                if person['u_id'] == u_id:
                    valid_token = True
            for person in channel['owners']:
                if person['u_id'] == u_id:
                    valid_token = True
    if not valid_user or not valid_channel or not valid_token:
        return False
    return True

def standup_start(token, channel_id, length):
    """start the standup queue"""
    channel_data = channel_datastore()
    if not check_inside_channel(token, channel_id):
        raise InputError(description="Channel is not valid")
    curr_time = datetime.now()
    timestamp = curr_time.replace(tzinfo=timezone.utc).timestamp()
    time_finish = timestamp + length
    for channel in channel_data:
        if channel['channel_id'] == channel_id:
            if channel['is_active']:
                raise InputError(description="standup is already setup")
            channel['is_active'] = True
            channel['time_finish'] = time_finish
    timer = threading.Timer(length, standup_end, kwargs={'channel_id':channel_id})
    timer.start()
    return {
        'time_finish': time_finish
    }

def standup_end(channel_id):
    """clear standup queue"""
    channel_data = channel_datastore()
    result = ''
    for channel in channel_data:
        if channel['channel_id'] == channel_id:
    ##here the standup time finished reset standup
            channel['is_active'] = False
            channel['time_finish'] = None
            if channel['standup'] == []:
                return {}
            for info in channel['standup']:
                result = result + info + "\n"
            channel['standup'] = []
            number_mess = len(channel['messages'])
            if number_mess == 0:
                message_id = channel_id * 100000
            else:
                message_prev = channel['messages'][number_mess - 1]
                message_id = message_prev['message_id'] + 1
    time_create = datetime.now().time()
    message_put = {
        'message_id': message_id,
        'message': result,
        'time_created':time_create,
    }
    for element in channel_data:
        if element['channel_id'] == channel_id:
            element['messages'].append(message_put)
    return {}

def standup_active(token, channel_id):
    """ask if standup is active in channel"""
    channel_data = channel_datastore()
    if not check_inside_channel(token, channel_id):
        raise InputError(description="Channel_id is not valid")
    for channel in channel_data:
        if channel['channel_id'] == channel_id:
            is_active = channel['is_active']
            time_finish = channel['time_finish']
    return {
        'is_active': is_active,
        'time_finish':time_finish
    }

def standup_send(token, channel_id, message):
    """send message to standup queue"""
    channel_data = channel_datastore()
    auth_data = auth_datastore()
    if not check_inside_channel(token, channel_id):
        raise AccessError(description="users not in the channel")
    if len(message) > 1000:
        raise InputError(description="message too long")
    for user in auth_data:
        if user['token'] == token:
            name_first = user['name_first']
            name_last = user['name_last']
    refine = name_first + " " + name_last + ": " + message
    for channel in channel_data:
        if channel['channel_id'] == channel_id:
            if not channel['is_active']:
                raise InputError(description="standup is not active")
            channel['standup'].append(refine)

    return {}
