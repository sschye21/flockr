"""this test was written to test the message_sendlater in message.py"""
from time import time, sleep
import pytest
from message import message_sendlater, message_edit, message_remove
from auth import auth_login, auth_register
from channels import channels_create
from data_stores import channel_datastore
from other import clear
from error import InputError, AccessError

#testing a successful message send later
def test_success_sendlater():
    """test that successfully sends a message at a specified time in the future"""
    clear()
    auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    login_user = auth_login("steven@gmail.com", "123456")
    token1 = login_user['token']
    channel_id = channels_create(token1, "Thurs09Mango", True)

    currtime = time() + 1.1
    message = "Hello World"

    message_id = message_sendlater(token1, channel_id, message, currtime)

    #this will pass time for x amount of seconds
    sleep(2)

    assert message_id == channel_id * 100000
    channel_data = channel_datastore()
    assert channel_data[0]['messages'][0]['message'] == "Hello World"

#assumption: user can edit his message that he has set even though it hasnt been sent yet
#test case where user wants to edit the message he set
def test_sendlater_edit():
    """success case where user edits the message after he set to send"""
    clear()
    auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    login_user = auth_login("steven@gmail.com", "123456")
    token1 = login_user['token']
    channel_id = channels_create(token1, "Thurs09Mango", True)

    message = "Hello World"
    currtime = time() + 0.1

    message_id = message_sendlater(token1, channel_id, message, currtime)
    message_edit(token1, message_id, "Goodbye World")

    sleep(2)

    assert message_id == channel_id * 100000

#test where user has an invalid token
def test_sendlater_invalidtoken():
    """fail test where user with invalid token tries to send message later"""
    clear()
    auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    login_user = auth_login("steven@gmail.com", "123456")
    token1 = login_user['token']
    token2 = "invalid token"
    channel_id = channels_create(token1, "Thurs09Mango", True)
    message = "Hello World"
    currtime = time() + 0.1

    with pytest.raises(AccessError):
        message_sendlater(token2, channel_id, message, currtime)

#test where user tries to send in an invalid channel
def test_sendlater_invalidchannel():
    """fail case where user tries to send later to an invalid channel"""
    clear()
    auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    login_user = auth_login("steven@gmail.com", "123456")
    token1 = login_user['token']
    channel_id = -3423423
    message = "Hello World"
    currtime = time() + 0.1

    with pytest.raises(InputError):
        message_sendlater(token1, channel_id, message, currtime)

#test where user tries to send an empty message later
def test_sendlater_empty():
    """fail case where user tries to send later an empty message string"""
    clear()
    auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    login_user = auth_login("steven@gmail.com", "123456")
    token1 = login_user['token']
    channel_id = channels_create(token1, "Thurs09Mango", True)
    message = ""
    currtime = time() + 0.1

    with pytest.raises(InputError):
        message_sendlater(token1, channel_id, message, currtime)

#test where the message is >1000 characters as specified in spec
def test_sendlater_toolong():
    """fail case where the message is too long"""
    clear()
    auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    login_user = auth_login("steven@gmail.com", "123456")
    token1 = login_user['token']
    channel_id = channels_create(token1, "Thurs09Mango", True)
    message = "s"*9876543
    currtime = time() + 0.1

    with pytest.raises(InputError):
        message_sendlater(token1, channel_id, message, currtime)

#test where the message has already been sent and is no longer scheduled
def test_message_alrsent():
    """fail case where the message has already been sent"""
    clear()
    auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    login_user = auth_login("steven@gmail.com", "123456")
    token1 = login_user['token']
    channel_id = channels_create(token1, "Thurs09Mango", True)
    message = "s"
    currtime = time() + 0.1
    sleep(2)

    with pytest.raises(InputError):
        message_sendlater(token1, channel_id, message, currtime)

#see assumptions.md
#test where message is removed before it is sent
def test_remove_sendlater():
    """fail case remove message before sending"""
    clear()
    auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    login_user = auth_login("steven@gmail.com", "123456")
    token1 = login_user['token']
    channel_id = channels_create(token1, "Thurs09Mango", True)

    message = "Hello World"
    currtime = time() + 0.1

    message_id = message_sendlater(token1, channel_id, message, currtime)

    with pytest.raises(InputError):
        message_remove(token1, message_id)
