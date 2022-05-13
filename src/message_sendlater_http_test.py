"""message_sendlater http tests"""
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import json
from datetime import datetime
import requests
import pytest
from other import clear
from system_helper_functions import reg_user, reg_user2, create_channel

# Use this fixture to get the URL of the server. It starts the server for you,
# so you don't need to.
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
#pylint: disable = W0621
#test successful sendlater function
def test_success_sendlater(url):
    '''success case where message is sent later'''
    clear()
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']

    message_info = {
        'token': user1['token'],
        'channel_id': channel_id,
        'message': "Hello World",
        'time_sent': datetime.now().timestamp() + 1.1
    }
    resp = requests.post(url + "/message/sendlater", json=message_info)

    assert json.loads(resp.text)['message_id'] == channel_id*100000
    sleep(2)
    info = {
        'token': user1['token'],
        'channel_id': channel_id,
        'start': 0
    }
    resp = requests.get(url + "/channel/messages", params=info)
    result = json.loads(resp.text)
    assert result['messages'][0] == "Hello World"

#test user is not a member of channel he wants to send message later in
def test_non_member(url):
    '400 error as user is not a member of specified channel'
    clear()
    reg_user(url)
    channel_id = create_channel(url)['channel_id']

    user2 = reg_user2(url)[1]
    message_info = {
        'token': user2['token'],
        'channel_id': channel_id,
        'message': "Hello World",
        'time_sent': datetime.now().timestamp() + 0.1
    }
    resp = requests.post(url + "/message/sendlater", json=message_info)

    assert json.loads(resp.text)['code'] == 400

#test user attempting to send invalid message
def test_invalid_message(url):
    '400 error where user sends an invalid message'
    clear()
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']

    message_info = {
        'token': user1['token'],
        'channel_id': channel_id,
        'message': "s"*998765,
        'time_sent': datetime.now().timestamp()
    }
    resp = requests.post(url + "/message/sendlater", json=message_info)

    assert json.loads(resp.text)['code'] == 400

#test user enters an invalid time to post
def test_invalid_timetopost(url):
    '400 error where time to post is not valid'
    clear()
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']

    message_info = {
        'token': user1['token'],
        'channel_id': channel_id,
        'message': "Hello World",
        'time_sent': datetime.now().timestamp() - 987654321
    }
    resp = requests.post(url + "/message/sendlater", json=message_info)

    assert json.loads(resp.text)['code'] == 400

#test user attempts to send message later to a non-existing channel
def test_invalid_channel(url):
    '400 error where channel does not exist'
    clear()
    user1 = reg_user(url)[0]
    create_channel(url)

    message_info = {
        'token': user1['token'],
        'channel_id': -12345678987654321,
        'message': "Hello World",
        'time_sent': datetime.now().timestamp()
    }
    resp = requests.post(url + "/message/sendlater", json=message_info)

    assert json.loads(resp.text)['code'] == 400
