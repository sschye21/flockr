"""http tests for message_unpin function within message/unpin in server.py"""
import json
import requests
from other import clear
#pylint: disable = W0611
from system_helper_functions import reg_user, reg_user2, create_channel, url

#pylint: disable = W0621
def test_success_unpin_http(url):
    """tests successful unpin of message"""
    clear()
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']

    message_info = {
        'token': user1['token'],
        'channel_id': channel_id,
        'message': "Hello World"
    }
    resp = requests.post(url + "/message/send", json=message_info)
    message_id = json.loads(resp.text)['message_id']

    pinning = {
        'token': user1['token'],
        'message_id': message_id,
    }
    resp = requests.post(url + "/message/pin", json=pinning)

    unpinning = {
        'token': user1['token'],
        'message_id': message_id,
    }
    resp = requests.post(url + "/message/unpin", json=unpinning)

    result = json.loads(resp.text)
    assert result == {}

#test where message is invalid
def test_message_invalid_http(url):
    """400 error as user has an invalid message_id"""
    user1 = reg_user(url)[0]
    login_info = {
        'email': "steven@gmail.com",
        'password':"123456"
    }
    requests.post(url + "/auth/login", json=login_info)

    channel_id = create_channel(url)['channel_id']
    message_info = {
        'token': user1['token'],
        'channel_id': channel_id,
        'message': "Hello World"
    }
    requests.post(url + "/message/send", json=message_info)
    message_id = 12345

    unpinning = {
        'token': user1['token'],
        'message_id': message_id,
    }
    result = requests.post(url + "/message/unpin", json=unpinning)

    assert json.loads(result.text)['code'] == 400

#test where message is already unpinned
def test_already_unpinned_http(url):
    """tests unpinning message again"""
    clear()
    user1 = reg_user(url)[0]
    login_info = {
        'email': "michael@gmail.com",
        'password':"123456"
    }
    requests.post(url + "/auth/login", json=login_info)

    channel_id = create_channel(url)['channel_id']
    message_info = {
        'token': user1['token'],
        'channel_id': channel_id,
        'message': "Hello World"
    }
    resp = requests.post(url + "/message/send", json=message_info)
    message_id = json.loads(resp.text)['message_id']

    unpinning = {
        'token': user1['token'],
        'message_id': message_id,
    }
    requests.post(url + "/message/unpin", json=unpinning)

    resp = requests.post(url + "/message/unpin", json=unpinning)
    assert json.loads(resp.text)['code'] == 400

#test where user is not a member
def test_not_member_http(url):
    """400 error as user is not part of specified channel"""
    clear()
    user1 = reg_user(url)[0]
    login_info = {
        'email': "steven@gmail.com",
        'password':"123456"
    }
    requests.post(url + "/auth/login", json=login_info)

    channel_id = create_channel(url)['channel_id']
    message_info = {
        'token': user1['token'],
        'channel_id': channel_id,
        'message': "Hello World"
    }
    resp = requests.post(url + "/message/send", json=message_info)
    message_id = json.loads(resp.text)['message_id']
    user2 = reg_user2(url)[1]

    unpinning = {
        'token': user2['token'],
        'message_id': message_id,
    }
    result = requests.post(url + "/message/unpin", json=unpinning)
    assert json.loads(result.text)['code'] == 400

#test where user is not an owner
def test_not_owner_http(url):
    """tests someone who is not owner unpins it"""
    clear()
    user1 = reg_user2(url)[0]

    channel_id = create_channel(url)['channel_id']

    join = {
        'token':user1['token'],
        'channel_id':channel_id,
        'u_id':user1['u_id']
    }
    requests.post(url + "/channel/join", json=join)

    message_info = {
        'token': user1['token'],
        'channel_id': channel_id,
        'message': "Hello World"
    }
    resp = requests.post(url + "/message/send", json=message_info)
    message_id = json.loads(resp.text)['message_id']

    unpinning = {
        'token': user1['token'],
        'message_id': message_id,
    }
    result = requests.post(url + "/message/unpin", params=unpinning)
    assert json.loads(result.text)['code'] == 500
