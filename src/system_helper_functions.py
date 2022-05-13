'helper functions file for system tests'
import re
import json
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import pytest
#pylint: disable = W0621
#pylint: disable = C0303
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

def reg_user(url): #pylint: disable=W0621
    'system test to create a user'
    user1 = {
        'email':"lucas.hzzheng@gmail.com",
        'password':"lucaszheng",
        'name_first': "Lucas",
        'name_last' :"Zheng"
    }
    requests.post(url + "/auth/register", json=user1)
    result = requests.get(url + "/auth/user_info")
    payload = result.json()
    return payload

def reg_user2(url): #pylint: disable=W0621
    'system test to create a user'
    user2 = {
        'email': "sidsat@gmail.com",
        'password':"sidsat123",
        'name_first':"Sid",
        'name_last':  "Sat"

    }
    requests.post(url + "/auth/register", json=user2)
    result = requests.get(url + "/auth/user_info")
    payload = result.json()
    return payload

def create_channel(url): #pylint: disable=W0621
    'system test to create a channel'

    result = requests.get(url + "/auth/user_info")
    user = result.json()
    channel = {
        'token': user[0]['token'],
        'name' :  "Mango04",
        'is_public': True

    }
    result = requests.post(url + "/channels/create", json=channel)
    payload = result.json()
    return payload

def login_user1(url):
    'login user1'
    login_info = {
        'email': "lucas.hzzheng@gmail.com",
        'password':"lucaszheng"
    }
    resp = requests.post(url + "/auth/login", json=login_info)
    result = json.loads(resp.text)
    return result

def send_message(url):
    '''message_send helper function for route'''
    user1 = reg_user(url)[0]
    channel_id = create_channel(url)['channel_id']
    ##send message
    message_info = {
        'token':user1['token'],
        'channel_id': channel_id,
        'message': "hello world"
    }
    resp = requests.post(url + "/message/send", json=message_info)
    payload = resp.json()
    return payload

def create_channel2(url):
    '''create a second channel'''
    result = requests.get(url + "/auth/user_info")
    user = result.json()
    channel = {
        'token': user[0]['token'],
        'name' :  "Mango05",
        'is_public': True

    }
    result = requests.post(url + "/channels/create", json=channel)
    payload = result.json()
    return payload
