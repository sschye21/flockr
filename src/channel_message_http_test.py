"""channel_messages http tests"""
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import json
import requests
import pytest
from other import clear
from system_helper_functions import reg_user, create_channel, reg_user2

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
def test_startmessages_http(url):
    """this test will succeed as the correct user is retrieving his messages"""
    clear()
    user1 = reg_user(url)[0]
    user2 = reg_user2(url)[1]
    channel_id = create_channel(url)['channel_id']
    invite = {
        'token':user1['token'],
        'channel_id':channel_id,
        'u_id':user2['u_id']
    }
    requests.post(url + "/channel/invite", json=invite)
    message_info = {
        'token':user2['token'],
        'channel_id':channel_id,
        'message':"Hello World"
    }
    requests.post(url + "/message/send", json=message_info)
    message = {
        'token': user1['token'],
        'channel_id': channel_id,
        'start': 0
    }
    resp = requests.get(url + "/channel/messages", params=message)
    result = json.loads(resp.text)
    assert len(result['messages']) == 1

def test_invalidchannel_http(url):
    """this test raises a 400 error as user is trying to access a non-existing channel"""
    clear()
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']

    message_info = {
        'token':user1['token'],
        'channel_id': channel_id,
        'message':"Hello World"
    }
    requests.post(url + "/message/send", json=message_info)

    message = {
        'token': user1['token'],
        'channel_id': -1,
        'start': 0
    }
    result = requests.get(url + "/channel/messages", params=message)

    assert json.loads(result.text)['code'] == 400

def test_notmember_http(url):
    """test for user with that is not part of channel raising 400"""
    clear()
    reg_user(url)
    user2 = reg_user2(url)[1]
    channel_id = create_channel(url)['channel_id']
    check = {
        'token': user2['token'],
        'channel_id': channel_id,
        'start': 0
    }

    result = requests.get(url + "/channel/messages", params=check)

    assert json.loads(result.text)['code'] == 400

def test_startgreater_http(url):
    """this will raise 400 error as the start is greater than the total no. of messages"""
    clear()
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']

    check = {
        'token': user1['token'],
        'channel_id': channel_id,
        'start': 23874
    }
    result2 = requests.get(url + "/channel/messages", params=check)

    assert json.loads(result2.text)['code'] == 400
