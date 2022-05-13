"""message_edit tests"""
import pytest
from error import AccessError, InputError
from data_stores import channel_datastore
from other import clear
from message import message_edit, message_send
from auth import auth_register, auth_login
from channels import channels_create
from channel import channel_join
##################
#   MESSAGE_EDIT #
##################
#pylint: disable = C0303
def test_message_edit():
    """test normal message edit"""
    clear()
    result = auth_register("b.li@gmail.com", "password", "brittany", "li")
    auth_login("b.li@gmail.com", "password")
    token = result['token']

    channel_id = channels_create(token, 'Thurs09Mango', True)
    message_id = message_send(token, channel_id, "hello world")
    message_edit(token, message_id, "goodbye world")  

    channel_store = channel_datastore()

    for element in channel_store:
        if element['channel_id'] == channel_id:
            message = element['messages']
    
    assert message[0]['message'] == 'goodbye world'
    clear()

#test where message is empty and user attempts to edit
def test_message_edit_empty():
    """test normal message edit empty"""
    clear()
    result = auth_register("b.li@gmail.com", "password", "brittany", "li")
    auth_login("b.li@gmail.com", "password")
    token = result['token']

    channel_id = channels_create(token, 'Thurs09Mango', True)
    message_id = message_send(token, channel_id, "hello world")
    message_edit(token, message_id, "")

    channel_store = channel_datastore()
    for element in channel_store:
        if element['channel_id'] == channel_id:
            number_mess = len(element['messages'])
    assert number_mess == 0
    clear()

#test where users no in channel try to edit message
def test_message_edit_invalid():
    """test users who are not in channel try to edit a message"""
    clear()
    result = auth_register("b.li@gmail.com", "password", "brittany", "li")
    token = result['token']
    channel_id = channels_create(token, 'Thurs09Mango', True)
    message_id = message_send(token, channel_id, "hello world") # owner of channel sent a message
    
    # second registered user who is not part of channel
    result2 = auth_register("hello@gmail.com", "password", "Tom", "Everest") 
    token2 = result2['token']

    # user who isn't part of the channel attempted to edit the message
    with pytest.raises(AccessError):
        message_edit(token2, message_id, "goodbye world") 
    clear()

#test where the owner edits the message but he didnt send the message
def test_owner_edits():
    """test where owner edits a message someone else sent"""
    clear()
    channel_store = channel_datastore()
    register_data = auth_register("steven@gmail.com", "password", "Steven", "Chye")
    auth_login("steven@gmail.com", "password")
    token1 = register_data['token']
    channel_id = channels_create(token1, 'Thurs09Mango', True)

    register_data2 = auth_register("guest@gmail.com", "password", "Guest", "Test")
    token2 = register_data2['token']
    channel_join(token2, channel_id)

    message_id = message_send(token2, channel_id, "hello world")
    message_edit(token1, message_id, "World Hello")

    for element in channel_store:
        if element['channel_id'] == channel_id:
            message = element['messages']
    
    assert message[0]['message'] == 'World Hello'
    clear()

#test to edit the same message twice
def test_edit_twice():
    """test normal message edit twice"""
    clear()
    result = auth_register("b.li@gmail.com", "password", "brittany", "li")
    auth_login("b.li@gmail.com", "password")
    token = result['token']

    channel_id = channels_create(token, 'Thurs09Mango', True)
    message_id = message_send(token, channel_id, "hello world")
    message_edit(token, message_id, "goodbye world")

    channel_store = channel_datastore()

    for element in channel_store:
        if element['channel_id'] == channel_id:
            message = element['messages']
    
    assert message[0]['message'] == 'goodbye world'
    clear()

#test where user tries to edit message but has invalidated token
def test_invalidtoken_edit():
    """test invalid token user tries to edit message but raises AccessError"""
    clear()
    result = auth_register("b.li@gmail.com", "password", "brittany", "li")
    auth_login("b.li@gmail.com", "password")
    token = result['token']
    token2 = "invalidated token"

    channel_id = channels_create(token, 'Thurs09Mango', True)
    message_id = message_send(token, channel_id, "hello world")
    with pytest.raises(AccessError):
        message_edit(token2, message_id, "goodbye world")

#test where message edited is too long
def test_too_long():
    '''messages is greater than 1000 characters'''
    clear()
    result = auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    auth_login("steven@gmail.com", "123456")
    token = result['token']

    channel_id = channels_create(token, 'Thurs09Mango', True)
    message_id = message_send(token, channel_id, "hello world")
    with pytest.raises(InputError):
        message_edit(token, message_id, "s"*97654)
