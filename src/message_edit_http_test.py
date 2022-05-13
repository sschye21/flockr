"""message_edit http tests"""
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
def test_message_edit(url):
    """test normal message edit"""
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']
    message_info = {
        'token':user1['token'],
        'channel_id': channel_id,
        'message': "Hello World"
    }
    result = requests.post(url + "/message/send", json=message_info)
    message_id = json.loads(result.text)['message_id']
    message = "Hello Santa"
    new_info = {
        'token': user1['token'],
        'message_id': message_id,
        'message': message
    }
    requests.put(url + "/message/edit", json=new_info)
    check = {
        'token':user1['token'],
        'channel_id':channel_id,
        'start':0
    }
    resp = requests.get(url + "/channel/messages", params=check)
    result = json.loads(resp.text)
    assert result['messages'][0] == "Hello Santa"

def test_message_invalid(url):
    """test message edit if unauthorised user edits message"""
    clear()
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']

    user2 = reg_user2(url)[1]
    # edit message
    message_info = {
        'token':user1['token'],
        'channel_id': channel_id,
        'message': "Hello World"
    }
    resp = requests.post(url + "/message/send", json=message_info)
    message_id = json.loads(resp.text)['message_id']
    new_info = {
        'token': user2['token'],
        'message_id': message_id,
        'message': "hello Santa"
    }
    resp = requests.put(url + "/message/edit", json=new_info)
    assert json.loads(resp.text)['code'] == 400
