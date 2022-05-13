'''channel functions'''
import auth
from error import InputError, AccessError
from data_stores import channel_datastore, auth_datastore

def check_channel_id_valid(channel_id):
    """check if channel_id is repeat"""
    channel_store = channel_datastore()
    repeat = False
    for element in channel_store:
        if element['channel_id'] == channel_id:
            repeat = True
    return repeat

# Given a token, return its u_id

def token_to_u_id(token):
    """given users token return his id"""
    auth_store = auth_datastore()
    for i in auth_store:
        if i['token'] == token:
            return i['u_id']
    return "token not found"

# CHANNEL_INVITE
# Invites a user (with user id u_id) to join a channel with ID channel_id.
def channel_invite(token, channel_id, u_id):
    """invite someone into channel"""
    channel_store = channel_datastore()
    auth_store = auth_datastore()
    if not auth.check_repeat_u_id(u_id):
        raise InputError(description="u_id not found")
    if not check_channel_id_valid(channel_id):
        raise InputError(description="channel_id not exist")
    owner_id = token_to_u_id(token)

    is_owner = False
    for element in channel_store:
        if element['channel_id'] == channel_id:
            for person in element['owners']: ## Only owners can invite others
                if person['u_id'] == owner_id:
                    is_owner = True
    if not is_owner:
        raise AccessError(description="The person invited you is not the owner of the channel")
    # Add invited person into channel members, create the details for the invited first
    for i in auth_store:
        if i['u_id'] == u_id:
            name_first = i['name_first']
            name_last = i['name_last']
    new_member = {
        'u_id': u_id,
        'name_first': name_first,
        'name_last': name_last,
    }

    for element in channel_store:
        if element['channel_id'] == channel_id:
            element['members'].append(new_member)

    return{}

# CHANNEL_DETAILS
# Given a channel with ID channel_id that the authorised user is part of,
# provides basic details about the channel.
def channel_details(token, channel_id):
    """View channel details"""
    channel_store = channel_datastore()
    if not check_channel_id_valid(channel_id):
        raise InputError(description="channel_id not exist")
    user_id = token_to_u_id(token)
    is_member = False
    owner_details = []
    members_details = []
    for element in channel_store:
        if element['channel_id'] == channel_id:
            name = element['name']
            for person in element['owners']:## Owners and members can see details
                owner_details.append(person)
                if person['u_id'] == user_id:
                    is_member = True
            for person in element['members']:
                members_details.append(person)
                if person['u_id'] == user_id:
                    is_member = True
            if not is_member:
                raise AccessError(description="Person not found in the channel")
    # With the correct channel ID, we return all the details
    return{
        'name': name,
        'owner_members': owner_details,
        'all_members': members_details,
    }

# CHANNEL_MESSAGES
# Given a channel_id that the authorised user is part of, return up to
# 50 messages between index "start" and "start + 50".
#pylint: disable = R0912
def channel_messages(token, channel_id, start):
    """View channel messages"""
    # Check if token is valid, if not, raise AccessError
    auth_data = auth_datastore()
    channel_store = channel_datastore()
    token_valid = False
    for i in auth_data:
        if i['token'] == token:
            token_valid = True
    if not token_valid:
        raise AccessError(description="Invalid Token")
    # Check if channel id exists
    if not check_channel_id_valid(channel_id):
        raise InputError(description="Channel ID does not exist")
    # Check if they are member/owner of channel.
    # Unauthorised member = accesserror
    messages_list = []
    user_id = token_to_u_id(token)
    is_member = False
    for element in channel_store:
        if element['channel_id'] == channel_id:
            messages_list = element['messages']
            for person in element['owners']: ## Owners and members can see details
                if person['u_id'] == user_id:
                    is_member = True
            for person in element['members']:
                if person['u_id'] == user_id:
                    is_member = True
            if not is_member:
                raise AccessError(description="Person not found in the channel")
    # If start is greater than blah blah blah  = inputerror
    if start > len(messages_list):
        raise InputError(description="Start exceeds the length of messages")
    if (len(messages_list) - start) < 50:
        end = -1##return all messages in that channel
        for element in channel_store:
            if element['channel_id'] == channel_id:
                if start == (len(messages_list) - 1):
                    rmessage = []
                    rmessage.append(element['messages'][start]['message'])
                else:
                    rmessage = []
                    for i in range(start, len(messages_list - 1)):
                        rmessage.append(element['messages'][i]['message'])
    else:
        end = start + 50
        for element in channel_store:
            if element['channel_id'] == channel_id:
                rmessage = []
                for i in range(start, (end -1)):
                    rmessage.append(element['messages'][i]['message'])
    return{
        'messages':rmessage,
        'start': start,
        'end': end,
    }
# CHANNEL_LEAVE
# Given a channel ID, the user removed as a member of this channel.
def channel_leave(token, channel_id):
    """Leave channel"""
    channel_member = {}
    channel_store = channel_datastore()
    auth_store = auth_datastore()
    # Ensuring a valid token
    for i in auth_store:
        if i['token'] == token:
            user = i
            channel_member = {
                'u_id': user['u_id'],
                'name_first': user['name_first'],
                'name_last': user['name_last'],
            }
    found = False
    channel_found = False
    for channel in channel_store:
        if channel['channel_id'] == channel_id:
            channel_found = True
            for person in channel['members']:
                if person['u_id'] == channel_member['u_id']:
                    del person
                    found = True
            for person in channel['owners']:
                if person['u_id'] == channel_member['u_id']:
                    found = True
            if not found:
                raise AccessError(description="Member is not in that room")
                # Channel_id does exist and therefore continue on to remove the user

    if not channel_found:
        raise InputError(description="Not a valid channel_id")

    return {}


# CHANNEL_JOIN
# Given a channel_id of a channel that the authorised user can join, adds them to that channel
# InputError when any of:Channel ID is not a valid channel
# AccessError whenchannel_id refers to a channel that is private
# (when the authorised user is not an admin)


#check token is valid // if its not valid -> exceeption / get channel_id
#/add user of that token to the token of the (valid)channel_id
#return listof all members, owner members and name
def channel_join(token, channel_id):
    """join the channel"""
    channel_member = {}
    channel_store = channel_datastore()
    auth_store = auth_datastore()

    # Ensuring a valid token
    valid_token = False
    for i in auth_store:
        if i['token'] == token:
            user = i
            channel_member = {
                'u_id': user['u_id'],
                'name_first': user['name_first'],
                'name_last': user['name_last'],
            }
            permission_id = user['permission_id']
            valid_token = True

    if not valid_token:
        raise AccessError(description="Not a valid token")

    for channel in channel_store:
        if channel['channel_id'] == channel_id:
            # channel_id is private
            if permission_id == 1:
                channel['owners'].append(channel_member)
                return {}

            if not channel['is_public']:
                raise AccessError(description="channel is private")
                # channel_id does exist and therefore continue on to append the user
            channel['members'].append(channel_member)
            return {}

    raise InputError(description="Not a valid channel_id")

# CHANNEL_ADDOWNER
# Makes user with user id u_id an owner of this channel.
def channel_addowner(token, channel_id, u_id):
    """add owners to channel"""
    channel_owner = {}
    auth_store = auth_datastore()
    channel_store = channel_datastore()

    #Ensuring a valid token, otherwise AccessError
    valid_token = False
    for i in auth_store:
        if i['token'] == token:
            valid_token = True

    if not valid_token:
        raise AccessError(description="Not a valid token")

    #Ensuring a valid ID, otherwise InputError
    valid_id = False
    for i in auth_store:
        if i['u_id'] == u_id:
            user = i
            channel_owner = {
                'u_id': user['u_id'],
                'name_first': user['name_first'],
                'name_last': user['name_last'],
            }
        valid_id = True

    if not valid_id:
        raise InputError(description="Not a valid_ID")

    # See if channel ID is a valid channel or not
    for chan in channel_store:
        if chan['channel_id'] == channel_id:
            if channel_owner in chan['owners']:
                raise InputError(description="Already owner")
            chan['owners'].append(channel_owner)
            for person in chan['members']:
                if person['u_id'] == u_id:
                    chan['members'].remove(person)
            return {}

    raise InputError(description="Not a valid channel ID")

# CHANNEL_REMOVEOWNER
# Removes user with user id u_id an owner of this channel.
def channel_removeowner(token, channel_id, u_id):
    """remove owners from channel"""
    auth_store = auth_datastore()
    channel_store = channel_datastore()

    #Ensuring a valid token, otherwise AccessError
    valid_token = False
    for i in auth_store:
        if i['token'] == token:
            valid_token = True

    if not valid_token:
        raise AccessError(description="Not a valid token")

    #Ensuring a valid ID, otherwise InputError
    valid_id = False
    for i in auth_store:
        if i['u_id'] == u_id:
            valid_id = True

    if not valid_id:
        raise InputError(description="Not a valid_ID")

    # See if channel ID is a valid channel or not
    user_isowner = False
    channel_found = False
    for channel in channel_store:
        if channel['channel_id'] == channel_id:
            channel_found = True
            if len(channel['owners']) == 1:
                if len(channel['members']) > 0:
                    raise InputError(description="Channel must have at least one owner")
                channel_store.remove(channel)
            for person in channel['owners']:
                if person['u_id'] == u_id:
                    channel['owners'].remove(person)
                    user_isowner = True

    if not user_isowner:
        raise InputError(description="User is not an owner of the channel")

    if not channel_found:
        raise InputError(description="Not a valid channel ID")
    return {}
####end of file
