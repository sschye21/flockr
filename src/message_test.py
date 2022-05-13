'''tests for message send and message remove'''
import pytest
from auth import auth_register
from message import message_send, message_remove
from other import clear
from channels import channels_create
from error import InputError, AccessError
from data_stores import channel_datastore
from channel import channel_invite
def test_message_send():
    """test normal message send"""
    clear()
    result = auth_register("lucas.hzzheng@gmail.com", "lucaszheng", "Lucas", "Zheng")
    token = result['token']
    channel_id = channels_create(token, 'Thurs09Mango', True)
    message_id = message_send(token, channel_id, "hello World")
    assert message_id == channel_id * 100000 + 0

def test_message_mul():
    """test if more tests are send"""
    clear()
    result = auth_register("lucas.hzzheng@gmail.com", "lucaszheng", "Lucas", "Zheng")
    token = result['token']
    channel_id = channels_create(token, 'Thurs09Mango', True)
    message_send(token, channel_id, "hello World")
    message_id = message_send(token, channel_id, "hello World")
    assert message_id == channel_id * 100000 + 1

def test_message_send_long():
    """test too long message"""
    clear()
    result = auth_register("lucas.hzzheng@gmail.com", "lucaszheng", "Lucas", "Zheng")
    token = result['token']
    channel_id = channels_create(token, 'Thurs09Mango', True)
    with pytest.raises(InputError):
        message_send(token, channel_id, "h"*1001)

def test_message_send_no_valid():
    """test users not in the channel but try to send a message"""
    clear()
    result = auth_register("lucas.hzzheng@gmail.com", "lucaszheng", "Lucas", "Zheng")
    token = result['token']
    channel_id = channels_create(token, 'Thurs09Mango', True)
    result2 = auth_register("nick.hzzheng@gmail.com", "lucaszheng", "Lucas", "Zheng")
    token2 = result2['token']
    with pytest.raises(AccessError):
        message_send(token2, channel_id, "hello, world")

def test_message_remove():
    """test remove message normal"""
    clear()
    result = auth_register("lucas.hzzheng@gmail.com", "lucaszheng", "Lucas", "Zheng")
    token = result['token']
    channel_id = channels_create(token, 'Thurs09Mango', True)
    message_id = message_send(token, channel_id, "hello World")
    message_remove(token, message_id)
    ##access datastore
    channel_store = channel_datastore()
    for element in channel_store:
        if element['channel_id'] == channel_id:
            number_mess = len(element['messages'])
    assert number_mess == 0

def test_message_remove_more():
    """test remove middle messgae"""
    clear()
    result = auth_register("lucas.hzzheng@gmail.com", "lucaszheng", "Lucas", "Zheng")
    token = result['token']
    channel_id = channels_create(token, 'Thurs09Mango', True)
    message_send(token, channel_id, "hello World1")##first message
    message_send(token, channel_id, "hello World2")
    message_id = message_send(token, channel_id, "hello World3")
    message_send(token, channel_id, "hello World4")
    message_remove(token, message_id)
    ##access datastore
    channel_store = channel_datastore()
    for element in channel_store:
        if element['channel_id'] == channel_id:
            number_mess = len(element['messages'])
    assert number_mess == 3
    assert message_id == channel_id*100000 + 2

def test_message_remove_null():
    """test remove message twice"""
    clear()
    result = auth_register("lucas.hzzheng@gmail.com", "lucaszheng", "Lucas", "Zheng")
    token = result['token']
    channel_id = channels_create(token, 'Thurs09Mango', True)
    message_id = message_send(token, channel_id, "hello World")
    message_remove(token, message_id)
    with pytest.raises(InputError):
        message_remove(token, message_id)

def test_message_remove_from_owner():
    """message is removed by owner not the sender"""
    clear()
    owner = auth_register("lucas.hzzheng@gmail.com", "lucaszheng", "Lucas", "Zheng")
    owner_token = owner['token']
    channel_id = channels_create(owner_token, 'Thurs09Mango', True)
    invited = auth_register("nick.hzzheng@gmail.com", "lucaszheng", "Lucas", "Zheng")
    invited_u_id = invited['u_id']
    invited_token = invited['token']
    channel_invite(owner_token, channel_id, invited_u_id)
    message_id = message_send(invited_token, channel_id, "hello World")
    message_remove(owner_token, message_id)
    channel_store = channel_datastore()
    for element in channel_store:
        if element['channel_id'] == channel_id:
            number_mess = len(element['messages'])
    assert number_mess == 0

def test_message_remove_from_sender():
    """message is removed by sender who is not an owner"""
    clear()
    owner = auth_register("lucas.hzzheng@gmail.com", "lucaszheng", "Lucas", "Zheng")
    owner_token = owner['token']
    channel_id = channels_create(owner_token, 'Thurs09Mango', True)
    invited = auth_register("nick.hzzheng@gmail.com", "lucaszheng", "Lucas", "Zheng")
    invited_u_id = invited['u_id']
    invited_token = invited['token']
    channel_invite(owner_token, channel_id, invited_u_id)
    message_id = message_send(invited_token, channel_id, "hello World")
    message_remove(invited_token, message_id)
    channel_store = channel_datastore()
    for element in channel_store:
        if element['channel_id'] == channel_id:
            number_mess = len(element['messages'])
    assert number_mess == 0

def test_message_remove_from_null():
    """message is removed by another member of the channel but not owner"""
    clear()
    owner = auth_register("lucas.hzzheng@gmail.com", "lucaszheng", "Lucas", "Zheng")
    owner_token = owner['token']
    channel_id = channels_create(owner_token, 'Thurs09Mango', True)
    invited = auth_register("nick.hzzheng@gmail.com", "lucaszheng", "Lucas", "Zheng")
    invited_u_id = invited['u_id']
    invited_token = invited['token']
    channel_invite(owner_token, channel_id, invited_u_id)
    message_id = message_send(owner_token, channel_id, "hello World")
    with pytest.raises(AccessError):
        message_remove(invited_token, message_id)
