"""http tests for message_react function within message/react in server.py"""
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import json
import requests
import pytest
from other import clear
from system_helper_functions import reg_user, reg_user2, create_channel

#pylint: disable = W0621
@pytest.fixture
def url():
    """generate a url"""
    url_re = re.compile(r' \* Running on ([^ ]*)')
    server = Popen(["python3", "src/server.py"], stderr=PIPE, stdout=PIPE)
    line = server.stderr.readline()
    local_url = url_re.match(line.decode())
    if local_url:
        yield local_url.group(1)
        # Terminate the server
        server.send_signal(signal.SIGINT)
        waited = 0
        while server.poll() is None and waited < 5:
            sleep(0.1)
            waited += 0.1
        if server.poll() is None:
            server.kill()
    else:
        server.kill()
        raise Exception("Couldn't get URL from local server")

#test successful case of reacting to a message
def test_react_http(url):
    """tests successful reaction of message"""
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

    reaction = {
        'token': user1['token'],
        'message_id': message_id,
        'react_id': 1
    }
    resp = requests.post(url + "/message/react", json=reaction)
    result = json.loads(resp.text)
    assert result == {}

#http test for user not a member of a specified channel
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

    reaction = {
        'token': user2['token'],
        'message_id': message_id,
        'react_id': 1
    }
    result = requests.post(url + "/message/react", json=reaction)
    assert json.loads(result.text)['code'] == 400

#test invalid react_id
def test_invalid_reactid_http(url):
    """400 error as invalid react_id is used"""
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

    reaction = {
        'token': user1['token'],
        'message_id': message_id,
        'react_id': 987321
    }
    result = requests.post(url + "/message/react", json=reaction)
    assert json.loads(result.text)['code'] == 400

#test user already reacted to message
def test_already_reacted_http(url):
    """400 error as user has already reacted to message"""
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

    reaction = {
        'token': user1['token'],
        'message_id': message_id,
        'react_id': 1
    }
    requests.post(url + "/message/react", json=reaction)

    resp = requests.post(url + "/message/react", json=reaction)
    assert json.loads(resp.text)['code'] == 400

#test invalid message id
def test_invalid_message_id(url):
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

    reaction = {
        'token': user1['token'],
        'message_id': message_id,
        'react_id': 1
    }
    result = requests.post(url + "/message/react", json=reaction)

    assert json.loads(result.text)['code'] == 400
