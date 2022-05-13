"""channel_join function http tests"""
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

def test_valid_join_http(url):
    """test normal join"""
    clear()

    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']
    joined = {
        'token':user1['token'],
        'channel_id': channel_id
    }
    requests.post(url + "/channel/join", json=joined)


def test_invalid_id_join_http(url):
    """test channel_id is not valid"""
    clear()

    user1 = reg_user(url)[0]
    joined = {
        'token':user1['token'],
        'channel_id': 123
    }

    resp = requests.post(url + "/channel/join", json=joined)
    assert json.loads(resp.text)['code'] == 400


def test_unauthorised_join_http(url):
    """test unauthorised users joining"""
    clear()

    user1 = reg_user(url)[0]
    user2 = reg_user2(url)[1]
    channel1_info = {
        'token':user1['token'],
        'name':"Room 28",
        'is_public': False
    }
    resp_c = requests.post(url + "/channels/create", json=channel1_info)
    channel_id = json.loads(resp_c.text)['channel_id']
    joined = {
        'token':user2['token'],
        'channel_id': channel_id
    }
    resp = requests.post(url + "/channel/join", json=joined)
    assert json.loads(resp.text)['code'] == 400
