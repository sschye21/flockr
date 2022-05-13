'this file include the server tests for password reset'
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import json
import requests
import pytest
from system_helper_functions import reg_user
from other import clear
from auth import id_generator


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


def test_invalidpassword(url):
    'test short password'
    clear()
    reg_user(url)

    code = id_generator()

    check2 = {
        'reset_code': code,
        'new_password': "a"
    }

    resp = requests.post(url + "/auth/passwordreset/reset", json=check2)

    payload = resp.json()

    assert payload['code'] == 400

def test_invalidresetcode(url):
    'test invalid reset code'
    clear()
    reg_user(url)
    check2 = {
        'reset_code': 'ABCDE',
        'new_password': "helloworld"
    }

    resp = requests.post(url + "/auth/passwordreset/reset", json=check2)
    assert json.loads(resp.text)['code'] == 400

def test_passwordreset(url):
    'creating a password reset'
    clear()
    user = reg_user(url)[0]

    check = {
        'email': user['email'],
    }

    requests.post(url + "/auth/passwordreset/request", json=check)
    result = requests.get(url + "/auth/resetcode")
    payload = result.json()
    for i in payload:
        if i['email'] == user['email']:
            code = i['reset_code']


    check2 = {
        'reset_code': code,
        'new_password': "helloworld"
    }

    requests.post(url + "/auth/passwordreset/reset", json=check2)
    result = requests.get(url + "/auth/user_info")
    payload = result.json()
    for i in payload:
        if i['email'] == user['email']:
            assert i['password'] == "helloworld"
