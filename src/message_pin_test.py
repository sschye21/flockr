"""this test was written to test the message_pin in message.py"""

import pytest
from channel import channel_join
from message import message_send, message_pin, message_remove
from auth import auth_login, auth_register
from other import clear
from channels import channels_create
from error import InputError, AccessError
from data_stores import channel_datastore

def test_success_pin():
    """success where a user successfully pins a message"""
    clear()
    # owner
    auth_register("michael@gmail.com", "123456", "Michael", "Comino")
    login_user = auth_login("michael@gmail.com", "123456")
    token1 = login_user['token']
    channel_id = channels_create(token1, "Thurs09Mango", True)

    # member
    auth_register("guest@gmail.com", "password", "Guest", "Test")
    login_user2 = auth_login("guest@gmail.com", "password")
    token2 = login_user2['token']
    channel_join(token2, channel_id)

    message = "where is this"
    message_id = message_send(token2, channel_id, message)

    message_pin(token1, message_id)
    channel_store = channel_datastore()

    for element in channel_store:
        if element['channel_id'] == channel_id:
            message = element['messages']

    assert message[0]['message_id'] == message_id
    assert message[0]['message'] == 'where is this'
    assert message[0]['pin'] is True

#test where message is invalid
def test_message_invalid():
    """message_id is not a valid message"""
    clear()
    auth_register("michael@gmail.com", "123456", "Michael", "Comino")
    login_user = auth_login("michael@gmail.com", "123456")
    token1 = login_user['token']
    channel_id = channels_create(token1, "Thurs09Mango", True)

    message = "Hello World"
    message_id = message_send(token1, channel_id, message)
    message_remove(token1, message_id)

    with pytest.raises(InputError):
        message_pin(token1, message_id)

#test where message is already pinned
def test_already_pinned():
    '''fail case where message has already been pinned'''
    clear()
    # owner
    auth_register("michael@gmail.com", "123456", "Michael", "Comino")
    login_user = auth_login("michael@gmail.com", "123456")
    token1 = login_user['token']
    channel_id = channels_create(token1, "Thurs09Mango", True)

    # member
    auth_register("guest@gmail.com", "password", "Guest", "Test")
    login_user2 = auth_login("guest@gmail.com", "password")
    token2 = login_user2['token']
    channel_join(token2, channel_id)

    message = "where is this"
    message_id = message_send(token2, channel_id, message)

    message_pin(token1, message_id)

    with pytest.raises(InputError):
        message_pin(token1, message_id)


def test_not_member():
    """the authorised user is not a member of the channel that the message is within"""
    clear()
    auth_register("michael@gmail.com", "123456", "Michael", "Comino")
    login_user = auth_login("michael@gmail.com", "123456")
    token1 = login_user['token']
    channel_id = channels_create(token1, "Thurs09Mango", True)

    auth_register("guest@gmail.com", "password", "Guest", "Test")
    login_user2 = auth_login("guest@gmail.com", "password")
    token2 = login_user2['token']

    message = "Hello World"
    message_id = message_send(token1, channel_id, message)

    with pytest.raises(AccessError):
        message_pin(token2, message_id)


def test_not_owner():
    """test that raises AccessError as user is not an owner"""
    clear()
    auth_register("michael@gmail.com", "123456", "Michael", "Comino")
    login_user = auth_login("michael@gmail.com", "123456")
    token1 = login_user['token']

    auth_register("guest@gmail.com", "password", "Guest", "Test")
    login_user2 = auth_login("guest@gmail.com", "password")
    token2 = login_user2['token']

    # Creates a channel and michael automatically becomes owner
    channel_id = channels_create(token1, "Thurs09Mango", True)
    # guest joins the channel as member
    channel_join(token2, channel_id)

    message = "Hello World"
    message_id = message_send(token1, channel_id, message)

    with pytest.raises(AccessError):
        message_pin(token2, message_id)
