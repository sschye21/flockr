'this file include the server tests for channels create'
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import json
import requests
import pytest
from system_helper_functions import reg_user, create_channel
from other import clear



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

def test_create(url):
    'creating a public channel'
    clear()
    reg_user(url)
    channel_id = create_channel(url)
    assert channel_id == {
        'channel_id': 1
    }

def test_create2(url):
    'creating a private channel'
    clear()
    user1 = reg_user(url)[0]
    channel = {
        'token': user1['token'],
        'name': "Mango04",
        'is_public':False
    }
    result = requests.post(url + "/channels/create", json=channel)
    payload = result.json()
    assert payload == {
        'channel_id': 1
    }

def test_create_longname(url):
    'raises 400 error if channel name is too long'
    clear()
    user1 = reg_user(url)[0]
    channel = {
        'token': user1['token'],
        'name': "abcdefghijklmnopqrstuvwxyz",
        'is_public':False
    }
    resp = requests.post(url + "/channels/create", json=channel)
    assert json.loads(resp.text)['code'] == 400
