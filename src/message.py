'''message functions'''
import threading
from datetime import datetime
from channel import token_to_u_id, check_channel_id_valid
from data_stores import channel_datastore, auth_datastore
from error import InputError, AccessError
#pylint: disable = C0301
#pylint: disable = R0914
def message_send(token, channel_id, message):
    """send a message to the channel"""
    channel_store = channel_datastore()
    if len(message) > 1000:
        raise InputError(description="Messages too long")
    user_id = token_to_u_id(token)
    is_member = False
    for element in channel_store:
        if element['channel_id'] == channel_id:
            number_mess = len(element['messages'])
            if number_mess == 0:
                message_id = channel_id * 100000
            else:
                message_prev = element['messages'][number_mess - 1]
                message_id = message_prev['message_id'] + 1
            ##assumptions, message can't exceed 100000 in a channel
            for person in element['owners']:
                if person['u_id'] == user_id:
                    is_member = True
            for person in element['members']:
                if person['u_id'] == user_id:
                    is_member = True
            if not is_member:
                raise AccessError(description="Person not found in the channel")
    time_create = datetime.now().time()
    message_put = {
        'message_id': message_id,
        'u_id': user_id,
        'message': message,
        'time_created':time_create,
        'reacts': [{'react_id': 1, 'u_ids': [], 'is_this_user_reacted': False}],
        'pin': False,
        'unpin': False
    }
    for element in channel_store:
        if element['channel_id'] == channel_id:
            element['messages'].append(message_put)
    return message_id

#removes message that has been sent within the channel
def message_remove(token, message_id):
    """remove a message sent by user"""
    ##remove the message match with message_id, then reassign the message_id
    user_id = token_to_u_id(token)
    message_found = False
    remove_valid = False
    channel_store = channel_datastore()
    channel_id = int(message_id/100000)
    for element in channel_store:
        if element['channel_id'] == channel_id:
            for person in element['owners']:
                if person['u_id'] == user_id:
                    remove_valid = True
            for message in element['messages']:
                if message['message_id'] == message_id:
                    message_found = True
                    if message['u_id'] == user_id:
                        remove_valid = True
                    if remove_valid:
                        ##remove the message
                        element['messages'].remove(message)
    if not message_found:
        raise InputError(description="Message not found")
    if not remove_valid:
        raise AccessError("token not valid")

#pylint:disable = R0912
def message_edit(token, message_id, message):
    """edit message"""
    # An owner can edit any message while a member can only edit their own message.
    channel_store = channel_datastore()
    auth_store = auth_datastore()

    # Ensuring a valid token, otherwise AccessError
    valid_token = False
    for i in auth_store:
        if i['token'] == token:
            valid_token = True

    if not valid_token:
        raise AccessError(description="Not a valid token")

    if len(message) > 1000:
        raise InputError(description="Messages too long")

    # Converting token to u_id
    for i in auth_store:
        if i['token'] == token:
            user_id = i['u_id']
    is_owner = False
    is_member = False
    own_message = False
    for channel in channel_store:
    #owners can edit any message.
        for person in channel['owners']:
            if person['u_id'] == user_id:
                is_owner = True
        for person in channel['members']:
            if person['u_id'] == user_id:
                is_member = True

        for i in range(0, len(channel['messages'])):
            if channel['messages'][i]['message_id'] == message_id:
                # Check if own message.
                if channel['messages'][i]['u_id'] == user_id and is_member:
                    own_message = True
                if is_owner or own_message:
                    if message == "":
                        del channel['messages'][i]
                    else:
                        time_create = datetime.now().time()#update time
                        edited_message = {
                            'message_id': message_id,
                            'u_id': user_id,
                            'message': message,
                            'time_created': time_create
                        }
                        channel['messages'][i] = edited_message
        if is_owner is False and is_member is False:
            raise AccessError(description="Person not found in the channel")

    return {}

def message_sendlater(token, channel_id, message, time_sent):
    '''send a message later'''
    channel_store = channel_datastore()
    auth_store = auth_datastore()

    # Ensuring a valid token, otherwise AccessError
    valid_token = False
    for i in auth_store:
        if i['token'] == token:
            valid_token = True
            user_id = i['u_id']

    if not valid_token:
        raise AccessError(description="Not a valid token")

    #check if channel exists
    if not check_channel_id_valid(channel_id):
        raise InputError(description="channel_id not exist")

    #check if message is greater than 1000 characters
    if len(message) > 1000 or len(message) < 1:
        raise InputError(description="Messages not appropriate length")

    #need to check if message has already been sent
    currtime = datetime.now().timestamp()
    if time_sent - currtime < 0:
        raise InputError(description="Message not found within scheduled messages")

    #check if they are in channel
    is_member = False
    for channel in channel_store:
        if channel['channel_id'] == channel_id:
            for person in channel['owners']: ## Owners and members can see details
                if person['u_id'] == user_id:
                    is_member = True
            for person in channel['members']:
                if person['u_id'] == user_id:
                    is_member = True
    if not is_member:
        raise AccessError(description="Person not found in the channel")

    for element in channel_store:
        if element['channel_id'] == channel_id:
            number_mess = len(element['messages'])
            if number_mess == 0:
                message_id = channel_id * 100000
            else:
                message_prev = element['messages'][number_mess - 1]
                message_id = message_prev['message_id'] + 1
    message_put = {
        'message_id': message_id,
        'u_id': user_id,
        'message': message,
        'time_created': time_sent,
        'reacts': [{
            'react_id': 1,
            'u_ids': [],
            'is_this_user_reacted': False
        }],
        'pin': False,
        'unpin': False
    }
    for channel in channel_store:
        if channel['channel_id'] == channel_id:
            channel['schedule'].append(message_put)
    timer = threading.Timer(time_sent - currtime, send_the_message, kwargs={'channel_id':channel_id, 'message_id':message_id})
    timer.start()

    return message_id

def send_the_message(channel_id, message_id):
    """when called this function will send a scheduled message"""
    channel_store = channel_datastore()
    for element in channel_store:
        if element['channel_id'] == channel_id:
            for message in element['schedule']:
                if message['message_id'] == message_id:
                    element['messages'].append(message)
                    element['schedule'].remove(message)
    return {}

#pylint: disable = R0914
def message_react(token, message_id, react_id):
    """react to message"""
    channel_store = channel_datastore()
    auth_store = auth_datastore()
    valid_unreact_id = [1]

    #check if token is valid
    valid_token = False
    for i in auth_store:
        if i['token'] == token:
            valid_token = True
    if not valid_token:
        raise AccessError("Not a valid token")
    
    #check if user is in channel
    channel_id = int(message_id/100000)
    is_member = False
    message_found = False
    existing_react = False
    user_id = token_to_u_id(token)
    #check if user is in the channel
    #pylint: disable = R1702

    if not check_channel_id_valid(channel_id):
        raise InputError("Channel ID does not exist")

    for element in channel_store:
        if element['channel_id'] == channel_id:
            for person in element['owners']:
                if person['u_id'] == user_id:
                    is_member = True
            for person in element['members']:
                if person['u_id'] == user_id:
                    is_member = True
        if not is_member:
            raise AccessError("Person not found in the channel")

        for i in range(0, len(element['messages'])):
            #check if message is within the channel
            if element['messages'][i]['message_id'] == message_id:
                message_found = True
                if react_id not in valid_unreact_id:
                    raise InputError("Invalid Reaction")
            if not message_found:
                raise InputError("Message not found within channel")

            for react in element['messages'][i]['reacts']:
                if react.get("u_ids") == user_id:
                    existing_react = True
                    raise InputError("User has already reacted")
                if existing_react is False:
                    if react.get("react_id") == react_id:
                        if react["u_ids"].count(user_id) > 0:
                            raise InputError
                        react["is_this_user_reacted"] = True
                        react['u_ids'].append(user_id)

    return {}

#message_unreact function
def message_unreact(token, message_id, react_id):
    """unreact to message"""
    channel_store = channel_datastore()
    auth_store = auth_datastore()
    valid_unreact_id = [1]

    #check if token is valid
    valid_token = False
    for i in auth_store:
        if i['token'] == token:
            valid_token = True
    if not valid_token:
        raise AccessError("Not a valid token")
    
    #check if user is in channel
    channel_id = int(message_id/100000)
    is_member = False
    message_found = False
    user_id = token_to_u_id(token)
    #check if user is in the channel
    #pylint: disable = R1702

    if not check_channel_id_valid(channel_id):
        raise InputError("Channel ID does not exist")

    for element in channel_store:
        if element['channel_id'] == channel_id:
            for person in element['owners']:
                if person['u_id'] == user_id:
                    is_member = True
            for person in element['members']:
                if person['u_id'] == user_id:
                    is_member = True
        if not is_member:
            raise AccessError("Person not found in the channel")

        for i in range(0, len(element['messages'])):
            #check if message is within the channel
            if element['messages'][i]['message_id'] == message_id:
                message_found = True
                if react_id not in valid_unreact_id:
                    raise InputError("Invalid Reaction")
            if not message_found:
                raise InputError("Message not found within channel")
            
            for react in element['messages'][i]['reacts']:
                if react["react_id"] == react_id:
                    if react["u_ids"].count(user_id) < 1:
                        raise InputError("Reaction does not exist")
                    react["is_this_user_reacted"] = False
                    react['u_ids'].remove(user_id)

    return {}

#message_pin function
def message_pin(token, message_id):
    """message pin"""
    channel_store = channel_datastore()
    auth_store = auth_datastore()

    # Ensuring a valid token, otherwise AccessError
    valid_token = False
    for i in auth_store:
        if i['token'] == token:
            valid_token = True

    if not valid_token:
        raise AccessError("Not a valid token")

    # Converting token to u_id
    for i in auth_store:
        if i['token'] == token:
            user_id = i['u_id']

    is_owner = False
    is_member = False
    message_found = False

    for channel in channel_store:
    #owners can edit any message.
        for person in channel['owners']:
            if person['u_id'] == user_id:
                is_owner = True
        for person in channel['members']:
            if person['u_id'] == user_id:
                is_member = True
            
        if is_owner and is_member:
            break

    if not is_owner:
        raise AccessError("Person is not an owner and can't pin messages")

    # this is going through the messages in the channel and seeing if it 
    # has been pinned before and raising an error or if pin is false and 
    # therefore changing it to true
    for channel in channel_store:
        for i in range(0, len(channel['messages'])):
            #check if message is within the channel
            if channel['messages'][i]['message_id'] == message_id:
                message_found = True
                if channel['messages'][i]['pin']:
                    raise InputError("User has already pinned")
                
                channel['messages'][i]['pin'] = True

    if not message_found:
        raise InputError("Message not found within channel")

    return {}

#message_unpin function
def message_unpin(token, message_id):
    """message unpin"""
    channel_store = channel_datastore()
    auth_store = auth_datastore()

    # Ensuring a valid token, otherwise AccessError
    valid_token = False
    for i in auth_store:
        if i['token'] == token:
            valid_token = True

    if not valid_token:
        raise AccessError("Not a valid token")

    # Converting token to u_id
    for i in auth_store:
        if i['token'] == token:
            user_id = i['u_id']

    is_owner = False
    is_member = False
    message_found = False

    # this is checking through the whole channel list for the all messages sent 
    # and seeing if the owner is apart of that group
    for channel in channel_store:
        #owners can edit any message.
        for person in channel['owners']:
            if person['u_id'] == user_id:
                is_owner = True
        for person in channel['members']:
            if person['u_id'] == user_id:
                is_member = True
            
        if is_owner and is_member:
            break

    if not is_owner:
        raise AccessError("Person is not an owner and can't unpin messages")

    # this is going through the messages in the channel and seeing if it 
    # has been pinned before and raising an error or if pin 
    # is false and therefore changing it to true
    for channel in channel_store:
        for i in range(0, len(channel['messages'])):
            #check if message is within the channel
            if channel['messages'][i]['message_id'] == message_id:
                message_found = True
                if channel['messages'][i]['unpin']:
                    raise InputError("User has already unpinned")
                
                channel['messages'][i]['unpin'] = True

    if not message_found:
        raise InputError("Message not found within channel")

    return {}
