"""this will test the message_react function within message.py"""

import pytest
from channel import channel_join
from message import message_react, message_send
from auth import auth_login, auth_register
from other import clear
from channels import channels_create
from error import InputError, AccessError
from data_stores import channel_datastore

#pylint: disable = C0303
#test where a user successfully reacts to a message
def test_success_react():
    """success where a user successfully reacts to a message"""
    clear()
    auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    login_user = auth_login("steven@gmail.com", "123456")
    token1 = login_user['token']
    u_id1 = login_user['u_id']
    channel_id = channels_create(token1, "Thurs09Mango", True)

    message = "Hello World"
    message_id = message_send(token1, channel_id, message)

    message_react(token1, message_id, 1)
    channel_store = channel_datastore()

    for element in channel_store:
        if element['channel_id'] == channel_id:
            message = element['messages']
    
    assert message[0]['message_id'] == message_id
    assert message[0]['message'] == 'Hello World'
    assert {'react_id': 1, 'u_ids': [u_id1], 'is_this_user_reacted': True} in message[0]['reacts']

#test where two different people react to the same message
def test_twopeople_react():
    """success where two users react to the same message"""
    clear()
    auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    login_user = auth_login("steven@gmail.com", "123456")
    token1 = login_user['token']
    u_id1 = login_user['u_id']
    channel_id = channels_create(token1, "Thurs09Mango", True)

    auth_register("guest@gmail.com", "password", "Guest", "Test")
    login_user2 = auth_login("guest@gmail.com", "password")
    token2 = login_user2['token']
    u_id2 = login_user2['u_id']
    channel_join(token2, channel_id)

    message = "Hello World"
    message_id = message_send(token1, channel_id, message)

    message_react(token1, message_id, 1)
    message_react(token2, message_id, 1)

    channel_store = channel_datastore()
    for element in channel_store:
        if element['channel_id'] == channel_id:
            message = element['messages']
    
    assert message[0]['message_id'] == message_id
    assert message[0]['message'] == 'Hello World'
    assert {
        'react_id': 1, 
        'u_ids': [u_id1, u_id2], 
        'is_this_user_reacted': True
    } in message[0]['reacts']

#test where user has an invalidated token
def test_invalidtoken():
    """fail case where user has an invalid token"""
    clear()
    auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    login_user = auth_login("steven@gmail.com", "123456")
    token1 = login_user['token']
    channel_id = channels_create(token1, "Thurs09Mango", True)

    auth_register("guest@gmail.com", "password", "Guest", "Test")
    auth_login("guest@gmail.com", "password")
    token2 = "invalid token"

    message = "Hello World"
    message_id = message_send(token1, channel_id, message)
    
    with pytest.raises(AccessError):
        message_react(token2, message_id, 1)

#test where user is not a member of the channel
def test_nonmember():
    """fail case where user is not member of channel but user tries to react"""
    clear()
    auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    login_user = auth_login("steven@gmail.com", "123456")
    token1 = login_user['token']
    channel_id = channels_create(token1, "Thurs09Mango", True)

    auth_register("guest@gmail.com", "password", "Guest", "Test")
    login_user2 = auth_login("guest@gmail.com", "password")
    token2 = login_user2['token']

    message = "Hello World"
    message_id = message_send(token1, channel_id, message)

    with pytest.raises(AccessError):
        message_react(token2, message_id, 1)

#test case where the react id is invalid
def test_react_invalid():
    """fail case where users' react id is invalid"""
    clear()
    auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    login_user = auth_login("steven@gmail.com", "123456")
    token1 = login_user['token']
    channel_id = channels_create(token1, "Thurs09Mango", True)
    
    message = "Hello World"
    message_id = message_send(token1, channel_id, message)

    with pytest.raises(InputError):
        message_react(token1, message_id, 987654321)

#test where user cannot react to a message twice
#assumption - see assumptions.md
def test_already_reacted():
    """fail case where user has already reacted to the message"""
    clear()
    auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    login_user = auth_login("steven@gmail.com", "123456")
    token1 = login_user['token']
    channel_id = channels_create(token1, "Thurs09Mango", True)
    
    message = "Hello World"
    message_id = message_send(token1, channel_id, message)
    message_react(token1, message_id, 1)

    with pytest.raises(InputError):
        message_react(token1, message_id, 1)

#test where channel_id is invalid and message_id is an invalid message
def test_invalidchannel_andmessage():
    """fail case where user has already reacted to the message"""
    clear()
    auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    login_user = auth_login("steven@gmail.com", "123456")
    token1 = login_user['token']

    message_id = 123

    with pytest.raises(InputError):
        message_react(token1, message_id, 1)
