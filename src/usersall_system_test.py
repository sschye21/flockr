'system test for usersall'
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import json
import urllib
import pytest
from system_helper_functions import reg_user



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

def test_usersall(url):
    'system test for usersall'

    user = reg_user(url)

    req = urllib.request.Request(
        url + "/users/all?token="+str(user[0]['token'])
    )

    req.get_method = lambda: 'GET'

    response = json.load(urllib.request.urlopen(req))

    assert response['users'][0]['u_id'] == user[0]['u_id']
    assert response['users'][0]['email'] == "lucas.hzzheng@gmail.com"
    assert response['users'][0]['name_first'] == "Lucas"
    assert response['users'][0]['name_last'] == "Zheng"
    assert response['users'][0]['handle_str'] == "lucaszheng"
