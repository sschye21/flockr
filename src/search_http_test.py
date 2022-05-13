'this file include the server tests for search'
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import json
import requests
import pytest
from system_helper_functions import reg_user, create_channel



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

def test_incorrectsearch(url):
    '''test not-matching query'''
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']
    ##send message
    message_info = {
        'token':user1['token'],
        'channel_id': channel_id,
        'message': "hello world"
    }
    requests.post(url + "/message/send", json=message_info)
    requests.post(url + "/message/send", json=message_info)

    check = {
        'token':user1['token'],
        'query_str': "incorrect"
    }
    resp_c = requests.get(url + "/search", params=check)
    result = json.loads(resp_c.text)
    assert result['messages'] == []

def test_search(url):
    '''test match case'''
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']
    ##send message
    message_info = {
        'token': user1['token'],
        'channel_id': channel_id,
        'message': "hello world"
    }

    requests.post(url + "/message/send", json=message_info)

    details = {
        'token': user1['token'],
        'query_str': "hello world"
    }

    resp = requests.get(url + "/search", params=details)
    result = json.loads(resp.text)
    assert result['messages'][0] == "hello world"
