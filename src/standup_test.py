'''standup tests'''
import time
import pytest
from error import InputError, AccessError
from standup import standup_active, standup_send, standup_start
from channels import channels_create
from auth import auth_register
from other import clear
from data_stores import channel_datastore
from channel import channel_invite

def test_standup_start():
    """test is_active key"""
    clear()
    result = auth_register("lucas.hzzheng@gamil.com", "lucaszheng", "Lucas", "Zheng")
    token = result['token']
    channel_id = channels_create(token, 'Room 28', True)
    assert not standup_active(token, channel_id)['is_active']
    assert standup_active(token, channel_id)['time_finish'] is None

    time_finish = standup_start(token, channel_id, 1)['time_finish']
    assert standup_active(token, channel_id)['is_active']
    assert time_finish == standup_active(token, channel_id)['time_finish']

def test_standup_start_c_id():
    """test invalid_channel_id"""
    clear()
    result = auth_register("lucas.hzzheng@gamil.com", "lucaszheng", "Lucas", "Zheng")
    token = result['token']
    with pytest.raises(InputError):
        standup_start(token, 123, 5)

def test_standup_start_repeat():
    """test start when already start"""
    clear()
    result = auth_register("lucas.hzzheng@gamil.com", "lucaszheng", "Lucas", "Zheng")
    token = result['token']
    channel_id = channels_create(token, 'Room 28', True)
    standup_start(token, channel_id, 1)
    with pytest.raises(InputError):
        standup_start(token, channel_id, 1)

def test_standup_is_active():
    """test if not valid channel id"""
    clear()
    result = auth_register("lucas.hzzheng@gamil.com", "lucaszheng", "Lucas", "Zheng")
    token = result['token']
    with pytest.raises(InputError):
        standup_active(token, 123)

def test_standup_send_1():
    """test invalid id"""
    clear()
    result = auth_register("lucas.hzzheng@gamil.com", "lucaszheng", "Lucas", "Zheng")
    token = result['token']
    channel_id = channels_create(token, 'Room 28', True)
    standup_start(token, channel_id, 1)
    with pytest.raises(AccessError):
        standup_send(token, 123, "hello")

def test_standup_send_2():
    """test invalid token"""
    clear()
    result = auth_register("lucas.hzzheng@gamil.com", "lucaszheng", "Lucas", "Zheng")
    token = result['token']
    channel_id = channels_create(token, 'Room 28', True)
    standup_start(token, channel_id, 1)
    with pytest.raises(AccessError):
        standup_send("invalid", channel_id, "hello")

def test_standup_send_3():
    """test long message"""
    clear()
    result = auth_register("lucas.hzzheng@gamil.com", "lucaszheng", "Lucas", "Zheng")
    token = result['token']
    channel_id = channels_create(token, 'Room 28', True)
    standup_start(token, channel_id, 1)
    with pytest.raises(InputError):
        standup_send(token, channel_id, "h"*1001)

def test_standup_send_4():
    """test inactive standup"""
    clear()
    result = auth_register("lucas.hzzheng@gamil.com", "lucaszheng", "Lucas", "Zheng")
    token = result['token']
    channel_id = channels_create(token, 'Room 28', True)
    with pytest.raises(InputError):
        standup_send(token, channel_id, "hello")

def test_standup_send_user1():
    """test one user send message"""
    clear()
    result = auth_register("lucas.hzzheng@gamil.com", "lucaszheng", "Lucas", "Zheng")
    token = result['token']
    channel_id = channels_create(token, 'Room 28', True)
    standup_start(token, channel_id, 1)
    standup_send(token, channel_id, "hello")
    channel_data = channel_datastore()
    for channel in channel_data:
        if channel['channel_id'] == channel_id:
            assert channel['standup'] == ["Lucas Zheng: hello"]
        time.sleep(2)
        assert channel['messages'][0]['message'] == "Lucas Zheng: hello\n"
        assert not standup_active(token, channel_id)['is_active']
        assert standup_active(token, channel_id)['time_finish'] is None

def test_complex_case():
    """test two users"""
    clear()
    channel_data = channel_datastore()
    result = auth_register("lucas.hzzheng@gamil.com", "lucaszheng", "Lucas", "Zheng")
    token = result['token']
    channel_id = channels_create(token, 'Room 28', True)
    invited = auth_register("nick.hzzheng@gamil.com", "lucaszheng", "Nick", "Zheng")
    u_id = invited['u_id']
    token2 = invited['token']
    channel_invite(token, channel_id, u_id)
    standup_start(token, channel_id, 1)
    standup_send(token, channel_id, "hello")
    standup_send(token2, channel_id, "world")

    for channel in channel_data:
        if channel['channel_id'] == channel_id:
            assert channel['standup'] == ["Lucas Zheng: hello", "Nick Zheng: world"]
        time.sleep(3)
        assert channel['messages'][0]['message'] == "Lucas Zheng: hello\nNick Zheng: world\n"
        assert not standup_active(token, channel_id)['is_active']
        assert standup_active(token, channel_id)['time_finish'] is None
    