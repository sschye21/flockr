"""http tests for message_unreact function within message/react in server.py"""
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

#test successful case of unreacting to a message
def test_react_http(url):
    """tests successful unreaction of message"""
    clear()
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']

    user2 = reg_user2(url)[1]
    joined = {
        'token':user2['token'],
        'channel_id': channel_id
    }
    requests.post(url + "/channel/join", json=joined)

    message_info = {
        'token': user1['token'],
        'channel_id': channel_id,
        'message': "Hello World"
    }
    resp = requests.post(url + "/message/send", json=message_info)
    message_id = json.loads(resp.text)['message_id']

    reaction = {
        'token': user2['token'],
        'message_id': message_id,
        'react_id': 1
    }
    requests.post(url + "/message/react", json=reaction)

    unreaction = {
        'token': user2['token'],
        'message_id': message_id,
        'react_id': 1
    }
    resp = requests.post(url + "/message/unreact", json=unreaction)
    result = json.loads(resp.text)
    assert result == {}

#test unreaction for a non-member
def test_unreact_non_member(url):
    """400 error as user is not a member of channel to unreact to message"""
    clear()
    user1 = reg_user(url)[0]
    user2 = reg_user2(url)[1]

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
    result = requests.post(url + "/message/react", json=reaction)

    unreaction = {
        'token': user2['token'],
        'message_id': message_id,
        'react_id': 1
    }
    result = requests.post(url + "/message/unreact", json=unreaction)
    assert json.loads(result.text)['code'] == 400

#test invalid message_id
def test_invalid_message_id(url):
    """400 error as a user has an invalid message_id that user is trying to unreact to"""
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
    result = requests.post(url + "/message/react", json=reaction)

    unreaction = {
        'token': user1['token'],
        'message_id': -1,
        'react_id': 1
    }
    result = requests.post(url + "/message/unreact", json=unreaction)
    assert json.loads(result.text)['code'] == 400
#test invalid react_id
def test_invalid_react_id(url):
    """400 error as user has an invalid react_id"""
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
    result = requests.post(url + "/message/react", json=reaction)

    unreaction = {
        'token': user1['token'],
        'message_id': message_id,
        'react_id': 98765432345678
    }
    result = requests.post(url + "/message/unreact", json=unreaction)
    assert json.loads(result.text)['code'] == 400
