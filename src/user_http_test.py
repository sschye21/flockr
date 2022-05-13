'''user_profile_http functions http tests'''
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import json
import requests
import pytest
from other import clear
from system_helper_functions import reg_user, reg_user2

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
def test_success_user_info(url):
    """test for successful return of information"""
    clear()
    user1 = reg_user(url)[0]
    check = {
        'token':user1['token'],
        'u_id':user1['u_id']
    }
    resp_c = requests.get(url + "user/user_profile", params=check)
    result = json.loads(resp_c.text)
    assert result['user']['name_first'] == 'Lucas'

def test_invalid_uid(url):
    """test for u_id is not a valid user -- input error"""
    clear()
    user1 = reg_user(url)[0]
    check = {
        'token':user1['token'],
        'u_id':10086
    }
    resp_c = requests.get(url + "user/user_profile", params=check)
    result = json.loads(resp_c.text)
    assert result['code'] == 400

#test for a successful update of handle
def test_change_handle(url):
    """change handle"""
    clear()
    user1 = reg_user(url)[0]
    replace_info = {
        'token':user1['token'],
        'handle_str': "MichaelC"
    }
    requests.put(url + "/user/profile/sethandle", json=replace_info)
    check = {
        'token':user1['token'],
        'u_id':user1['u_id']
    }
    resp_c = requests.get(url + "user/user_profile", params=check)
    result = json.loads(resp_c.text)['user']
    assert result['handle_str'] == "MichaelC"

def test_handle_short(url):
    """test where handle entered is less than 3 characters"""
    clear()
    user1 = reg_user(url)[0]
    replace_info = {
        'token':user1['token'],
        'handle_str': "MC"
    }
    resp = requests.put(url + "/user/profile/sethandle", json=replace_info)
    result = json.loads(resp.text)
    assert result['code'] == 400

def test_handle_long(url):
    """test where handle entered is more than 20 characters"""
    clear()
    user1 = reg_user(url)[0]
    replace_info = {
        'token':user1['token'],
        'handle_str': "M"*21
    }
    resp = requests.put(url + "/user/profile/sethandle", json=replace_info)
    result = json.loads(resp.text)
    assert result['code'] == 400

def test_handle_3(url):
    """test where handle entered is 3 characters"""
    clear()
    user1 = reg_user(url)[0]
    replace_info = {
        'token':user1['token'],
        'handle_str': "M"*3
    }
    requests.put(url + "/user/profile/sethandle", json=replace_info)
    check = {
        'token':user1['token'],
        'u_id':user1['u_id']
    }
    resp_c = requests.get(url + "user/user_profile", params=check)
    result = json.loads(resp_c.text)['user']
    assert result['handle_str'] == "MMM"

def test_handle_20(url):
    """test where handle entered is 20 characters"""
    clear()
    user1 = reg_user(url)[0]
    replace_info = {
        'token':user1['token'],
        'handle_str': "M"*20
    }
    requests.put(url + "/user/profile/sethandle", json=replace_info)
    check = {
        'token':user1['token'],
        'u_id':user1['u_id']
    }
    resp_c = requests.get(url + "user/user_profile", params=check)
    result = json.loads(resp_c.text)['user']
    assert result['handle_str'] == "M"*20

def test_invalid_token(url):
    """test where user has an invalid token but attempts to change handle"""
    clear()
    token2 = "invalid token"
    replace_info = {
        'token':token2,
        'handle_str': "M"*20
    }
    resp = requests.put(url + "/user/profile/sethandle", json=replace_info)
    result = json.loads(resp.text)
    assert result['code'] == 400

def test_handle_taken(url):
    """test where user attempts to change handle but another user already has that handle"""
    clear()
    user1 = reg_user(url)[0]
    user2 = reg_user2(url)[1]
    replace_info = {
        'token':user2['token'],
        'handle_str': "MichaelC"
    }
    requests.put(url + "/user/profile/sethandle", json=replace_info)
    replace_info = {
        'token':user1['token'],
        'handle_str': "MichaelC"
    }
    resp = requests.put(url + "/user/profile/sethandle", json=replace_info)
    result = json.loads(resp.text)
    assert result['code'] == 400

def test_changeemail_http(url):
    """test for successful change of email address for user"""
    clear()
    user1 = reg_user(url)[0]
    update = {
        'token':user1['token'],
        'email': "guest@gmail.com"
    }
    resp = requests.put(url + "/user/profile/setemail", json=update)
    check = {
        'token': user1['token'],
        'u_id': user1['u_id']
    }
    resp = requests.get(url + "user/user_profile", params=check)
    result = json.loads(resp.text)['user']
    assert result['email'] == "guest@gmail.com"

#test for changing email to same email
def test_sameemail_http(url):
    """test where user changes email to the same one"""
    clear()
    user1 = reg_user(url)[0]
    update = {
        'token':user1['token'],
        'email': "steven@gmail.com"
    }
    result = requests.put(url + "/user/profile/setemail", json=update)
    check = {
        'token': user1['token'],
        'u_id': user1['u_id']
    }
    resp = requests.get(url + "user/user_profile", params=check)
    result = json.loads(resp.text)['user']
    assert result['email'] == "steven@gmail.com"

#test where email is update is in invalid form
def test_invalidform_http(url):
    """test that raises 400 error as email is not in required form"""
    clear()
    user1 = reg_user(url)[0]
    check = {
        'token':user1['token'],
        'email': "guest.com@gmail"
    }
    result = requests.put(url + "/user/profile/setemail", json=check)
    assert json.loads(result.text)['code'] == 400

#invalid token test
def test_invalidtoken_http(url):
    """test that raises 400 error as user has an invalid token"""
    clear()
    reg_user(url)
    check = {
        'token':"token1",
        'email': "guest@gmail.com"
    }
    result = requests.put(url + "/user/profile/setemail", json=check)
    assert json.loads(result.text)['code'] == 400

########################
# USER_PROFILE_SETNAME #
########################
def test_name_change(url):
    """test where there is a successful change of the firstname and lastname"""
    clear()
    user1 = reg_user(url)[0]

    update = {
        'token':user1['token'],
        'name_first': "Guest",
        'name_last': "Test"
    }
    result = requests.put(url + "/user/profile/setname", json=update)

    check = {
        'token': user1['token'],
        'u_id': user1['u_id']
    }
    resp = requests.get(url + "user/user_profile", params=check)
    result = json.loads(resp.text)['user']
    assert result['name_first'] == "Guest"
    assert result['name_last'] == "Test"

#test where user has an invalid token
def test_invalid_token_setname(url):
    """test that raises 400 error as invalid token is used"""
    clear()
    reg_user(url)
    update = {
        'token':"invalid",
        'name_first': "Guest",
        'name_last': "Test"
    }
    result = requests.put(url + "/user/profile/setname", json=update)
    assert json.loads(result.text)['code'] == 400

#test where first and last name are invalid as it is too long
def test_toolong_name(url):
    """test raises 400 error as first and last name are > than 50 characters"""
    clear()
    user1 = reg_user(url)[0]
    update = {
        'token':user1['token'],
        'name_first': "S"*98234,
        'name_last': "C"*3428374
    }
    result = requests.put(url + "/user/profile/setname", json=update)
    assert json.loads(result.text)['code'] == 400

#test where first and last name are invalid as they are too short
def test_tooshort_name(url):
    """test raises 400 error as first and last name are < than 1 character"""
    clear()
    user1 = reg_user(url)[0]
    update = {
        'token':user1['token'],
        'name_first': "",
        'name_last': ""
    }
    result = requests.put(url + "/user/profile/setname", json=update)
    assert json.loads(result.text)['code'] == 400
