'''this test is related to channel_messages from channel.py'''
import pytest
from error import InputError, AccessError
from auth import auth_register, auth_login
from channel import channel_messages
from channels import channels_create
from message import message_send
from other import clear
def test_start_messages():
    """returning the first start+50 messages sent"""
    clear()
    auth_register("guest@gmail.com", "123456", "Steven", "Chye")
    login_user = auth_login("guest@gmail.com", "123456")
    token1 = login_user['token']
    #assuming the channel we create is public, register the user to the channel
    channel_id = channels_create(token1, "Thurs09Mango", True)
    #loop that will send 50 messages to the channel to be returned
    i = 0
    while i <= 50:
        message_send(token1, channel_id, str(i))
        i += 1
    message_start = channel_messages(token1, channel_id, 0)
    assert message_start['start'] == 0 and message_start['end'] == 50

def test_invalid_channel():
    """testing a non-existing channel"""
    clear()
    auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    login_user = auth_login("steven@gmail.com", "123456")
    token1 = login_user['token']
    with pytest.raises(InputError):
        channel_messages(token1, "Fri09Grapefruit", 0)
#when returns least recent messages in channel returning -1 as "end"
#indicating no more messages to load
def test_more_than_50_messages():
    """send more than 50 messages"""
    clear()
    auth_register("michael@gmail.com", "123456", "Michael", "Michael")
    login_user = auth_login("michael@gmail.com", "123456")
    token1 = login_user['token']
    #assuming the channel we create is public, register the user to the channel
    channel_id = channels_create(token1, "Thu09Mango", True)
    #loop that will send 50 messages to the channel to be returned
    i = 0
    while i <= 50:
        message_send(token1, channel_id, "H")
        i += 1
    with pytest.raises(InputError):
        channel_messages(token1, "Thurs09Mango", -1)

def test_token_invalid():
    """user trying to enter a channel with an invalid token"""
    clear()
    auth_register("brittany@gmail.com", "123456", "Brittany", "Brittany")
    login_user = auth_login("brittany@gmail.com", "123456")
    token1 = login_user['token']
    #assuming the channel we create is public, register the user to the channel
    channel_id = channels_create(token1, "Thu09Mango", True)
    #loop that will send 50 messages to the channel to be returned
    i = 0
    while i <= 50:
        message_send(token1, channel_id, str(i))
        i += 1
    token2 = "Invalid Token"
    with pytest.raises(AccessError):
        channel_messages(token2, "Thurs09Mango", 0)

def test_start_greater_than_total_messages():
    """#messages sent are greater than 50"""
    clear()
    auth_register("sidd@gmail.com", "123456", "Sidd", "Sidd")
    login_user = auth_login("sidd@gmail.com", "123456")
    token1 = login_user['token']
    #assuming the channel we create is public, register the user to the channel
    channel_id = channels_create(token1, "Thu09Mango", True)
    #loop that will send 50 messages to the channel to be returned
    i = 0
    while i <= 50:
        message_send(token1, channel_id, str(i))
        i += 1
    with pytest.raises(InputError):
        channel_messages(token1, channel_id, 52)

def test_unauthorised_user():
    """#test unauthorised user trying to enter the channel he is not part of"""
    clear()
    auth_register("lucas@gmail.com", "123456", "Lucas", "Lucas")
    login_user = auth_login("lucas@gmail.com", "123456")
    token1 = login_user['token']
    #assuming the channel we create is public, register the user to the channel
    channel_id = channels_create(token1, "Thu09Mango", True)
    #loop that will send 50 messages to the channel to be returned
    i = 0
    while i <= 50:
        message_send(token1, channel_id, str(i))
        i += 1
    unauthorised_user2 = auth_register("other@gmail.com", "Password", "Bob", "Rob")
    token2 = unauthorised_user2['token']
    with pytest.raises(AccessError):
        channel_messages(token2, channel_id, 0)
