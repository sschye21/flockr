"""this will test the message_unreact function within message.py"""

import pytest
from message import message_react, message_send, message_unreact
from auth import auth_login, auth_register
from other import clear
from channels import channels_create
from error import InputError, AccessError
from data_stores import channel_datastore

#pylint: disable = C0303
#test for a successful unreaction to a message
def test_success_unreact():
    """success where a user successfully unreacts to a message"""
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
    assert {
        'react_id': 1, 
        'u_ids': [u_id1], 
        'is_this_user_reacted': True
    } in message[0]['reacts']

    message_unreact(token1, message_id, 1)
    assert message[0]['message_id'] == message_id
    assert message[0]['message'] == 'Hello World'
    assert {
        'react_id': 1, 
        'u_ids': [], 
        'is_this_user_reacted': False
    } in message[0]['reacts']

#test where user has an invalid token
def test_invalid_token():
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
        message_unreact(token2, message_id, 1)

#test where user is not a member of specified channel
def test_nonmember():
    """fail case where user is not member of channel but user tries to unreact"""
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
        message_unreact(token2, message_id, 1)

#test where there is no existing reaction to message
def test_no_reaction():
    """fail case where user has not reacted to message"""
    clear()
    auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    login_user = auth_login("steven@gmail.com", "123456")
    token1 = login_user['token']
    channel_id = channels_create(token1, "Thurs09Mango", True)

    message = "Hello World"
    message_id = message_send(token1, channel_id, message)

    with pytest.raises(InputError):
        message_unreact(token1, message_id, 1)

#test where user tries to unreact twice
def test_unreact_twice():
    """fail case where user has already unreacted to the message"""
    clear()
    auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    login_user = auth_login("steven@gmail.com", "123456")
    token1 = login_user['token']
    channel_id = channels_create(token1, "Thurs09Mango", True)
    
    message = "Hello World"
    message_id = message_send(token1, channel_id, message)
    message_react(token1, message_id, 1)
    
    message_unreact(token1, message_id, 1)

    with pytest.raises(InputError):
        message_unreact(token1, message_id, 1)

#test where channel does not exist and message_id is invalid
def test_invalid_channel_andmessage():
    """fail case where channel and message_id does not exist"""
    clear()
    auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    login_user = auth_login("steven@gmail.com", "123456")
    token1 = login_user['token']
    message_id = 123

    with pytest.raises(InputError):
        message_unreact(token1, message_id, 1)

#test where unreact_id is invalid
def test_invalid_unreact_id():
    """fail case where unreact_id is invalid"""
    clear()
    auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    login_user = auth_login("steven@gmail.com", "123456")
    token1 = login_user['token']
    channel_id = channels_create(token1, "Thurs09Mango", True)
    
    message = "Hello World"
    message_id = message_send(token1, channel_id, message)
    message_react(token1, message_id, 1)

    with pytest.raises(InputError):
        message_unreact(token1, message_id, 98765)
