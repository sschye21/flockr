'''change permission id function http tests'''
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import json
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
def test_first_user(url):
    """test if first user come up with permission id with 1"""
    clear()
    user1 = reg_user(url)[0]
    assert user1['permission_id'] == 1

def test_second_user(url):
    """test if second user has permission id 2"""
    clear()
    reg_user(url)
    user2 = reg_user2(url)[1]
    assert user2['permission_id'] == 2

def test_change_permission_id(url):
    """change second user permission id to 1"""
    clear()
    user1 = reg_user(url)[0]
    user2 = reg_user2(url)[1]
    change = {
        'token': user1['token'],
        'u_id':user2['u_id'],
        'permission_id':1
    }
    requests.post(url + '/admin/userpermission/change', json=change)
    result = requests.get(url + "/auth/user_info")
    payload = result.json()
    assert payload[1]['permission_id'] == 1

def test_auto_owner(url):
    """person with p_id 1 always be owner of a channel"""
    clear()
    user1 = reg_user(url)[0]
    user2 = reg_user2(url)[1]
    channel_id = create_channel(url)['channel_id']
    invitation = {
        'token': user1['token'],
        'channel_id':channel_id,
        'u_id': user2['u_id']
    }
    requests.post(url + '/channel/invite', json=invitation)
    change = {
        'token': user1['token'],
        'u_id':user2['u_id'],
        'permission_id':1
    }
    requests.post(url + '/admin/userpermission/change', json=change)
    result = requests.get(url + "/channel/channel_info")
    payload = result.json()
    assert payload[0]['owners'][1]['u_id'] == user2['u_id']

def test_auto_owner_without_invite(url):
    """person with p_id = 1 join a channel become a owner auto"""
    user1 = reg_user(url)[0]
    user2 = reg_user2(url)[1]
    channel_id = create_channel(url)['channel_id']
    change = {
        'token': user1['token'],
        'u_id':user2['u_id'],
        'permission_id':1
    }
    requests.post(url + "/admin/userpermission/change", json=change)
    joined = {
        'token':user2['token'],
        'channel_id': channel_id
    }
    requests.post(url + "/channel/join", json=joined)
    result = requests.get(url + "/channel/channel_info")
    payload = result.json()
    assert payload[0]['owners'][1]['u_id'] == user2['u_id']

def test_invalid_permission(url):
    """test raises InputError as user has invalid permission_id"""
    clear()
    user1 = reg_user(url)[0]
    user2 = reg_user2(url)[1]
    change = {
        'token': user1['token'],
        'u_id':user2['u_id'],
        'permission_id':3
    }
    resp = requests.post(url+ "/admin/userpermission/change", json=change)
    assert json.loads(resp.text)['code'] == 400
#test where user has an invalid u_id
def test_invalid_uid(url):
    """test raises InputError as user has an invalid u_id"""
    clear()
    user1 = reg_user(url)[0]
    change = {
        'token': user1['token'],
        'u_id':12345,
        'permission_id':1
    }
    resp = requests.post(url + "/admin/userpermission/change", json=change)
    assert json.loads(resp.text)['code'] == 400

#test where user is not an owner
def test_not_an_owner(url):
    """test that raises AccessError as user is not an owner"""
    clear()
    user1 = reg_user(url)[0]
    user2 = reg_user2(url)[1]
    change = {
        'token': user2['token'],
        'u_id':user1['u_id'],
        'permission_id':1
    }

    resp = requests.post(url + "/admin/userpermission/change", json=change)
    assert json.loads(resp.text)['code'] == 400
