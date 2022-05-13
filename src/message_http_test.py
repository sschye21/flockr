'''channel_invite and channel_details functions http tests'''
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
def test_message_send(url):
    """test normal message send"""
    clear()
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']
    ##send message
    message_info = {
        'token':user1['token'],
        'channel_id': channel_id,
        'message': "hello world"
    }
    resp = requests.post(url + "/message/send", json=message_info)
    assert json.loads(resp.text)['message_id'] == channel_id*100000 + 0

def test_message_mul(url):
    """test if more tests are send"""
    clear()
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']
    ##send message
    message_info = {
        'token':user1['token'],
        'channel_id': channel_id,
        'message': "hello world"
    }
    requests.post(url + "/message/send", json=message_info)
    resp = requests.post(url + "/message/send", json=message_info)
    assert json.loads(resp.text)['message_id'] == channel_id*100000 + 1

def test_message_send_long(url):
    """test too long message"""
    clear()
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']
    ##send message
    message_info = {
        'token':user1['token'],
        'channel_id': channel_id,
        'message': "h"*10000
    }
    resp = requests.post(url + "/message/send", json=message_info)
    assert json.loads(resp.text)['code'] == 400

def test_message_send_no_valid(url):
    """test users not in the channel but try to send a message"""
    clear()
    reg_user(url)
    channel_id = create_channel(url)['channel_id']
    user2 = reg_user2(url)[1]
    message_info = {
        'token':user2['token'],
        'channel_id': channel_id,
        'message': "h"*10000
    }
    resp = requests.post(url + "/message/send", json=message_info)
    assert json.loads(resp.text)['code'] == 400

def test_message_remove(url):
    """test remove message normal"""
    clear()
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']
    message_info = {
        'token':user1['token'],
        'channel_id': channel_id,
        'message': "hello world"
    }
    resp = requests.post(url + "/message/send", json=message_info)
    message_id = json.loads(resp.text)['message_id']
    remove_info = {
        'token': user1['token'],
        'message_id':message_id
    }
    requests.delete(url + "/message/remove", json=remove_info)
    ##access datastore
    result = requests.get(url + "/channel/channel_info")
    payload = result.json()
    assert len(payload[0]['messages']) == 0

def test_message_remove_more(url):
    """test remove middle messgae"""
    clear()
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']
    message_info = {
        'token':user1['token'],
        'channel_id': channel_id,
        'message': "hello world"
    }
    requests.post(url + "/message/send", json=message_info)##first message

    requests.post(url + "/message/send", json=message_info)

    resp = requests.post(url + "/message/send", json=message_info)
    message_id = json.loads(resp.text)['message_id']

    requests.post(url + "/message/send", json=message_info)
    remove_info = {
        'token':user1['token'],
        'message_id': message_id
    }
    requests.delete(url + "/message/remove", json=remove_info)
    assert message_id == channel_id*100000 + 2

def test_message_remove_null(url):
    """test remove message twice"""
    clear()
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']
    message_info = {
        'token':user1['token'],
        'channel_id': channel_id,
        'message': "hello world"
    }
    resp = requests.post(url + "/message/send", json=message_info)
    message_id = json.loads(resp.text)['message_id']
    remove_info = {
        'token':user1['token'],
        'message_id': message_id
    }
    requests.delete(url + "/message/remove", json=remove_info)
    resp = requests.delete(url + "/message/remove", json=remove_info)
    assert json.loads(resp.text)['code'] == 400

def test_message_remove_from_owner(url):
    """message is removed by owner not the sender"""
    clear()
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']
    user2 = reg_user2(url)[1]
    ##invitation
    invitation = {
        'token': user1['token'],
        'channel_id': channel_id,
        'u_id': user2['u_id']
    }
    requests.post(url + "/channel/invite", json=invitation)
    message_info = {
        'token':user1['token'],
        'channel_id': channel_id,
        'message': "hello world"
    }
    resp = requests.post(url + "/message/send", json=message_info)
    message_id = json.loads(resp.text)['message_id']
    remove_info = {
        'token':user1['token'],
        'message_id': message_id
    }
    requests.delete(url + "/message/remove", json=remove_info)
     ##access datastore
    payload = requests.get(url + "/channel/channel_info").json()
    assert len(payload[0]['messages']) == 0

def test_message_remove_from_sender(url):
    """message is removed by sender who is not an owner"""
    clear()
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']
    user2 = reg_user2(url)[1]
    ##invitation
    invitation = {
        'token': user1['token'],
        'channel_id': channel_id,
        'u_id': user2['u_id']
    }
    requests.post(url + "/channel/invite", json=invitation)
    message_info = {
        'token':user2['token'],
        'channel_id': channel_id,
        'message': "hello world"
    }
    resp = requests.post(url + "/message/send", json=message_info)
    message_id = json.loads(resp.text)['message_id']
    remove_info = {
        'token':user2['token'],
        'message_id':message_id
    }
    requests.delete(url + "/message/remove", json=remove_info)
     ##access datastore
    result = requests.get(url + "/channel/channel_info")
    payload = result.json()
    assert len(payload[0]['messages']) == 0

def test_message_remove_from_null(url):
    """message is removed by another member of the channel but not owner"""
    clear()
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']
    user2 = reg_user2(url)[1]
    ##invitation
    invitation = {
        'token': user1['token'],
        'channel_id': channel_id,
        'u_id': user2['u_id']
    }
    requests.post(url + "/channel/invite", json=invitation)
    message_info = {
        'token':user1['token'],
        'channel_id': channel_id,
        'message': "hello world"
    }
    resp = requests.post(url + "/message/send", json=message_info)
    message_id = json.loads(resp.text)['message_id']
    remove_info = {
        'token':user2['token'],
        'message_id':message_id
    }
    resp = requests.delete(url + "/message/remove", json=remove_info)
    assert json.loads(resp.text)['code'] == 400
