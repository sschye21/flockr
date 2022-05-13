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
#############################################################
#                   CHANNELS_LISTALL                           #
#############################################################
def test_channel_listall(url):
    'test function for channels list'
    clear()
    user1 = reg_user(url)[0]
    user2 = reg_user2(url)[1]
    channel_id1 = create_channel(url)['channel_id']
    channel2_info = {
        'token':user2['token'],
        'name':"Room 289",
        'is_public':False
    }
    resp_c = requests.post(url + "/channels/create", json=channel2_info)
    channel_id2 = json.loads(resp_c.text)['channel_id']
    check = {
        'token': user1['token']
    }
    resp_c = requests.get(url + "channels/listall", params=check)
    all_channels = json.loads(resp_c.text)['channels']
    id_collect = []
    for channels in all_channels:
        id_collect.append(channels['channel_id'])
    assert channel_id1 == id_collect[0]
    assert channel_id2 == id_collect[1]
