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

##################
# CHANNEL_INVITE #
##################


#pylint: disable = W0621

def test_channel_invite(url):
    """test normal invitation"""
    clear()
    result = requests.get(url + "/channel/channel_info")
    payload = result.json()
    assert payload == []
    ##my first channel
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']
    user2 = reg_user2(url)[1]
    ##invitation
    invitation = {
        'token': user1['token'],
        'channel_id':channel_id,
        'u_id': user2['u_id']
    }
    requests.post(url + "/channel/invite", json=invitation)
    ##check if my member is in the channel.
    result = requests.get(url + "/channel/channel_info")
    payload = result.json()
    assert payload[0]['members'][0]['name_first'] == user2['name_first']

def test_channel_invite_c_id(url):
    """test channel_id is not valid"""
    clear()
    user1 = reg_user(url)[0]
    user2 = reg_user2(url)[1]
    invitation = {
        'token': user1['token'],
        'channel_id':123,
        'u_id': user2['u_id']
    }
    resp = requests.post(url + "/channel/invite", json=invitation)
    assert json.loads(resp.text)['code'] == 400

def test_channel_invite_u_id(url):
    """test if invalid u_id works"""
    clear()
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']
    invitation = {
        'token': user1['token'],
        'channel_id':channel_id,
        'u_id': 10086
    }
    resp = requests.post(url + "/channel/invite", json=invitation)
    assert json.loads(resp.text)['code'] == 400

def test_channel_invite_not_auth(url):
    """test if invalid token can invite"""
    clear()
    reg_user(url)
    channel_id = create_channel(url)['channel_id']
    user2 = reg_user2(url)[1]
    ##invitation
    invitation = {
        'token': user2['token'],
        'channel_id':channel_id,
        'u_id': user2['token']
    }
    resp = requests.post(url + "/channel/invite", json=invitation)
    assert json.loads(resp.text)['code'] == 400

###################
# CHANNEL_DETAILS #
###################

def test_channel_details(url):
    """test normal channel details"""
    clear()
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']
    check = {
        'token':user1['token'],
        'channel_id':channel_id
    }
    resp_c = requests.get(url + "channel/details", params=check)
    result = json.loads(resp_c.text)
    assert result['owner_members'][0]['name_first'] == user1['name_first']

def test_channel_details_with_invited(url):
    """test when invited member in the channel"""
    clear()
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']
    user2 = reg_user2(url)[1]
    ##invitation
    invitation = {
        'token': user1['token'],
        'channel_id':channel_id,
        'u_id': user2['u_id']
    }
    requests.post(url + "/channel/invite", json=invitation)
    check = {
        'token':user1['token'],
        'channel_id':channel_id
    }
    resp_c = requests.get(url +"channel/details", params=check)
    result = json.loads(resp_c.text)
    assert result['all_members'][0]['name_first'] == user2['name_first']

def test_channel_details_channel_id(url):
    """test if channel_id is not found"""
    clear()
    user1 = reg_user(url)[0]
    check = {
        'token':user1['token'],
        'channel_id':100
    }
    resp_c = requests.get(url + "channel/details", params=check)
    result = json.loads(resp_c.text)
    assert result['code'] == 400

def test_channel_details_not_auth(url):
    """test if token is not valid"""
    clear()
    reg_user(url)
    channel_id = create_channel(url)['channel_id']
    user2 = reg_user2(url)[1]
    check = {
        'token':user2['token'],
        'channel_id':channel_id
    }
    resp_c = requests.get(url + "channel/details", params=check)
    result = json.loads(resp_c.text)
    assert result['code'] == 400

#############
# ADD_OWNER #
#############

def test_make_owner(url):
    """# Register two users."""
    clear()
    # Register first user
    user1 = reg_user(url)[0]
    # Register second user
    user2 = reg_user2(url)[1]
    # Create a channel
    channel_id = create_channel(url)['channel_id']
    # Bob automatically becomes owner as he created the channel
    # Sam joins the channel and becomes member
    joined = {
        'token': user2['token'],
        'channel_id': channel_id
    }
    requests.post(url + "/channel/join", json=joined)
    # Promote Sam to become owner of the same channel
    addinfo = {
        'token':user1['token'],
        'channel_id': channel_id,
        'u_id': user2['u_id']
    }
    requests.post(url + "/channel/addowner", json=addinfo)
    # Check to see if Sam has become owner
    check = {
        'token':user1['token'],
        'channel_id':channel_id
    }
    resp_c = requests.get(url + "channel/details", params=check)
    result = json.loads(resp_c.text)
    assert result['owner_members'][1]['name_first'] == user2['name_first']

def test_invalid_id(url):
    """# Channel ID is not valid."""
    clear()
    user1 = reg_user(url)[0]
    # Register second user
    user2 = reg_user2(url)[1]
    # Channel_addowner function is called but there is no channel_id yet
    # First user attempts to add owner
    addinfo = {
        'token':user1['token'],
        'channel_id': 123,
        'u_id':user2['u_id']
    }
    resp = requests.post(url + "/channel/addowner", json=addinfo)
    result = json.loads(resp.text)
    assert result['code'] == 400

def test_already_owner(url):
    """# User is already owner of this channel. """
    clear()
    # Register user
    user1 = reg_user(url)[0]
    # Creates a channel and Bob automatically becomes owner
    channel_id = create_channel(url)['channel_id']
    addinfo = {
        'token':user1['token'],
        'channel_id': channel_id,
        'u_id':user1['u_id']
    }
    resp = requests.post(url + "/channel/addowner", json=addinfo)
    result = json.loads(resp.text)
    assert result['code'] == 400

def test_invalid_token_add(url):
    """# Token is invalid. """
    clear()
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']
    addinfo = {
        'token':"invalid_token",
        'channel_id': channel_id,
        'u_id':user1['u_id']
    }
    resp = requests.post(url + "/channel/addowner", json=addinfo)
    result = json.loads(resp.text)
    assert result['code'] == 400

################
# REMOVE_OWNER #
################


def test_remove_owner(url):
    """# Remove an owner in which they revert back to being a member."""
    # Register first user
    clear()
    user1 = reg_user(url)[0]
    # Register second user
    user2 = reg_user2(url)[1]
    # Create a channel
    channel_id = create_channel(url)['channel_id']
    # Bob automatically becomes owner as he created the channel
    # Sam joins the channel and becomes member
    joined = {
        'token':user2['token'],
        'channel_id': channel_id
    }
    requests.post(url + "/channel/join", json=joined)
    # Promote Sam to become owner of the same channel
    addinfo = {
        'token': user1['token'],
        'channel_id':channel_id,
        'u_id' : user2['u_id']
    }
    requests.post(url + "/channel/addowner", json=addinfo)
    # Bob removes Sam from being owner of the same channel
    removeinfo = {
        'token':user1['token'],
        'channel_id':channel_id,
        'u_id':user2['u_id']
    }
    requests.post(url + "/channel/removeowner", json=removeinfo)
    # Check to see if Sam is still owner
    check = {
        'token':user1['token'],
        'channel_id':channel_id
    }
    resp_c = requests.get(url +"channel/details", params=check)
    result = json.loads(resp_c.text)
    assert len(result['owner_members']) == 1

def test_invalid_id_remove(url):
    """# Not a valid channel_id."""
    clear()
    # Register first user who does not create a channel
    user1 = reg_user(url)[0]
    # Register second user
    user2 = reg_user2(url)[1]
    # Channel_removeowner function is called but there is no channel_id yet
    # First user attempts to remove owner
    removeinfo = {
        'token':user1['token'],
        'channel_id': 123,
        'u_id': user2['u_id']
    }
    resp = requests.post(url + "/channel/removeowner", json=removeinfo)
    result = json.loads(resp.text)
    assert result['code'] == 400

def test_remove_not_owner(url):
    """# User with user id is not an owner of the channel."""
    clear()
    # Register first user who does not create a channel
    user1 = reg_user(url)[0]
    # Register second user
    user2 = reg_user2(url)[1]
    # Creates a channel and Bob automatically becomes owner
    channel_id = create_channel(url)['channel_id']
    # Sam joins the channel as member
    joined = {
        'token': user2['token'],
        'channel_id':channel_id
    }
    requests.post(url + "/channel/join", json=joined)
    removeinfo = {
        'token':user1['token'],
        'channel_id': channel_id,
        'u_id':user2['u_id']
    }
    resp = requests.post(url + "/channel/removeowner", json=removeinfo)
    result = json.loads(resp.text)
    assert result['code'] == 400
# Token is invalid.

def test_invalid_token_remove(url):
    """test invalid token"""
    clear()
    # Register first user who does not create a channel
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']
    removeinfo = {
        'token':"invalid",
        'channel_id':channel_id,
        'u_id': user1['u_id']
    }
    resp = requests.post(url + "/channel/removeowner", json=removeinfo)
    result = json.loads(resp.text)
    assert result['code'] == 400
