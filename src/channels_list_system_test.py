'''channel_invite and channel_details functions http tests'''
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import json
import requests
import pytest
from other import clear
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
#############################################################
#                   CHANNELS_LIST                           #
#############################################################

def test_channel_list(url):
    'test function for channels list'
    clear()

    user1 = reg_user(url)[0]
    create_channel(url)
    check = {
        'token': user1['token']
    }
    resp_c = requests.get(url + "channels/list", params=check)
    result = json.loads(resp_c.text)
    assert result['channels'][0]['channel_id'] == 1
