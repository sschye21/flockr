'''standup functions http tests'''
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
def test_standup_start(url):
    """test is_active key"""
    clear()
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']
    check = {
        'token':user1['token'],
        'channel_id':channel_id
    }
    resp = requests.get(url + "/standup/active", params=check)
    result = json.loads(resp.text)
    assert not result['is_active']
    assert result['time_finish'] is None
    info = {
        'token':user1['token'],
        'channel_id':channel_id,
        'length':1
    }
    resp = requests.post(url + "/standup/start", json=info)
    time_finish = json.loads(resp.text)['time_finish']
    resp = requests.get(url + "/standup/active", params=check)
    result = json.loads(resp.text)
    assert result['is_active']
    assert result['time_finish'] == time_finish
    sleep(1)

def test_standup_start_c_id(url):
    """test invalid_channel_id"""
    clear()
    user1 = reg_user(url)[0]
    info = {
        'token':user1['token'],
        'channel_id':123,
        'length':1
    }
    resp = requests.post(url + "/standup/start", json=info)
    result = json.loads(resp.text)
    assert result['code'] == 400

def test_standup_start_repeat(url):
    """test start when already start"""
    clear()
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']
    info = {
        'token':user1['token'],
        'channel_id':channel_id,
        'length':1
    }
    requests.post(url + "/standup/start", json=info)
    resp = requests.post(url + "/standup/start", json=info)
    result = json.loads(resp.text)
    assert result['code'] == 400

def test_standup_is_active(url):
    """test if not valid channel id"""
    clear()
    user1 = reg_user(url)[0]
    check = {
        'token':user1['token'],
        'channel_id':123
    }
    resp = requests.get(url + "/standup/active", params=check)
    result = json.loads(resp.text)
    assert result['code'] == 400

def test_standup_send_1(url):
    """test invalid id"""
    clear()
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']
    info = {
        'token':user1['token'],
        'channel_id':channel_id,
        'length':1
    }
    requests.post(url + "/standup/start", json=info)
    check = {
        'token':user1['token'],
        'channel_id':123,
        'message':"hello"
    }
    resp = requests.post(url + "/standup/send", json=check)
    result = json.loads(resp.text)
    assert result['code'] == 400
    sleep(1)

def test_standup_send_2(url):
    """test invalid token"""
    clear()
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']
    info = {
        'token':user1['token'],
        'channel_id':channel_id,
        'length':1
    }
    requests.post(url + "/standup/start", json=info)
    check = {
        'token':"invalid",
        'channel_id':channel_id,
        'message':"hello"
    }
    resp = requests.post(url + "/standup/send", json=check)
    result = json.loads(resp.text)
    assert result['code'] == 400
    sleep(1)

def test_standup_send_3(url):
    """test long message"""
    clear()
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']
    info = {
        'token':user1['token'],
        'channel_id':channel_id,
        'length':1
    }
    requests.post(url + "/standup/start", json=info)
    check = {
        'token':user1['token'],
        'channel_id':channel_id,
        'message':"h"*1001
    }
    resp = requests.post(url + "/standup/send", json=check)
    result = json.loads(resp.text)
    assert result['code'] == 400
    sleep(1)

def test_standup_send_4(url):
    """test inactive standup"""
    clear()
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']
    check = {
        'token':user1['token'],
        'channel_id':channel_id,
        'message':"hello"
    }
    resp = requests.post(url + "/standup/send", json=check)
    result = json.loads(resp.text)
    assert result['code'] == 400
    sleep(1)

def test_standup_send_user1(url):
    """test one user send message"""
    clear()
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']
    info = {
        'token':user1['token'],
        'channel_id':channel_id,
        'length':1
    }
    requests.post(url + "/standup/start", json=info)
    check = {
        'token':user1['token'],
        'channel_id':channel_id,
        'message':"hello"
    }
    resp = requests.post(url + "/standup/send", json=check)
    result = requests.get(url + "/channel/channel_info")
    payload = result.json()
    channel = payload[0]
    assert channel['standup'] == ["Lucas Zheng: hello"]
    sleep(3)
    check = {
        'token':user1['token'],
        'channel_id':channel_id
    }
    resp = requests.get(url + "/standup/active", params=check)
    result = json.loads(resp.text)
    assert not result['is_active']
    assert result['time_finish'] is None

def test_complex_case(url):
    """test two users"""
    clear()
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']
    user2 = reg_user2(url)[1]
    invitation = {
        'token': user1['token'],
        'channel_id':channel_id,
        'u_id': user2['u_id']
    }
    requests.post(url + "/channel/invite", json=invitation)
    info = {
        'token':user1['token'],
        'channel_id':channel_id,
        'length':1
    }
    requests.post(url + "/standup/start", json=info)
    check = {
        'token':user1['token'],
        'channel_id':channel_id,
        'message':"hello"
    }
    requests.post(url + "/standup/send", json=check)
    check = {
        'token':user2['token'],
        'channel_id':channel_id,
        'message':"world"
    }
    requests.post(url + "/standup/send", json=check)
    sleep(3)
    info = {
        'token': user1['token'],
        'channel_id': channel_id,
        'start': 0
    }
    resp = requests.get(url + "/channel/messages", params=info)
    result = json.loads(resp.text)
    assert result['messages'][0] == "Lucas Zheng: hello\nSid Sat: world\n"
