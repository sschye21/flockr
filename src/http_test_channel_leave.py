"""channel_leave function http tests"""
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

def test_valid_leave_http(url):
    """test normal leave"""
    clear()

    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']
    left = {
        'token':user1['token'],
        'channel_id':channel_id
    }
    requests.post(url + "/channel/leave", json=left)



def test_invalid_id_leave_http(url):
    """test channel_id is not valid"""
    clear()

    user1 = reg_user(url)[0]
    left = {
        'token':user1['token'],
        'channel_id':123
    }

    resp = requests.post(url + "/channel/leave", json=left)
    assert json.loads(resp.text)['code'] == 400



def test_not_channel_member_http(url):
    """ test not a channel member """
    clear()

    reg_user(url)
    channel_id = create_channel(url)['channel_id']

    user2 = reg_user2(url)[1]

    left = {
        'token':user2['token'],
        'channel_id':channel_id
    }
    resp = requests.post(url + "/channel/leave", json=left)
    assert json.loads(resp.text)['code'] == 400
