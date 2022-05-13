'''auth_regiter function http tests'''
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import json
import requests
import pytest
from other import clear
from system_helper_functions import reg_user, login_user1


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
def test_login_correct(url):
    """test if login works"""
    clear()
    user1 = reg_user(url)[0]
    login_info = {
        'email': "lucas.hzzheng@gmail.com",
        'password':"lucaszheng"
    }
    resp = requests.post(f"{url}/auth/login", json=login_info)
    result = json.loads(resp.text)['u_id']
    assert result == user1['u_id']

#test for unsuccessful login using the wrong password
def test_wrongpassword_login(url):
    """this test will raise 400 error as the wrong password is entered"""
    clear()
    user1 = reg_user(url)[0]
    login_info = {
        'email': user1['email'],
        'password': "helloword"
    }
    result = requests.post(f"{url}/auth/login", json=login_info)
    assert json.loads(result.text)['code'] == 400

#test for unsuccessful login using the wrong email
def test_incorrectemail_login(url):
    """this test will raise 400 error as the wrong email is entered"""
    clear()
    user1 = reg_user(url)[0]
    login_info = {
        'email':"michael@gmail.com",
        'password': user1['password']
    }
    result = requests.post(f"{url}/auth/login", json=login_info)
    assert json.loads(result.text)['code'] == 400

#test for unsuccessful login due to no registered account
def test_noregistration_login(url):
    """this test will raise 400 error as there is no registered account"""
    clear()
    login_info = {
        'email': "michael@gmail.com",
        'password': "123456"
    }
    result = requests.post(f"{url}/auth/login", json=login_info)
    assert json.loads(result.text)['code'] == 400

#test for unsuccessful login due to incorrect email and password
def test_everythingincorrect_login(url):
    """test raises 400 error due to incorrect email and password entered"""
    clear()
    reg_user(url)
    login_info = {
        'email':  "guest@gmail.com",
        'password': "password"
    }
    result = requests.post(f"{url}/auth/login", json=login_info)
    assert json.loads(result.text)['code'] == 400



def test_logout_success(url):
    """logout is successful"""
    clear()
    user1 = reg_user(url)[0]
    login_user1(url)
    logout_info = {
        'token': user1['token']
    }
    resp = requests.post(f"{url}/auth/logout", json=logout_info)
    result = json.loads(resp.text)
    assert result['is_success']

def test_logout_failed(url):
    """invalid token"""
    clear()
    reg_user(url)
    logout_info = {
        'token': "invalid_token"
    }
    resp = requests.post(f"{url}/auth/logout", json=logout_info)
    result = json.loads(resp.text)
    assert result['code'] == 400

def test_auth_register(url):
    """test normal user register"""
    clear()
    ##test if my user are empty in the beginning
    result = requests.get(f"{url}/auth/user_info")
    payload = result.json()
    assert payload == []
    ##my first user
    user1 = reg_user(url)[0]
    assert user1['email'] == "lucas.hzzheng@gmail.com"

def test_auth_register_e(url):
    """test user register with invalid email"""
    clear()
    user2 = {
        'email':"lucas.hzzhengcom",
        'password':"lucaszheng",
        'name_first': "Lucas",
        'name_last':"Zheng"
    }
    resp = requests.post(f"{url}/auth/register", json=user2)
    assert json.loads(resp.text)['code'] == 400

def test_auth_register_p(url):
    """test user register with shorter password"""
    clear()
    user2 = {
        'email':"lucas.hzzheng@gamilcom",
        'password':"l",
        'name_first': "Lucas",
        'name_last':"Zheng"
    }
    resp = requests.post(f"{url}/auth/register", json=user2)
    assert json.loads(resp.text)['code'] == 400

def test_auth_register_n(url):
    """test user register without first_name"""
    clear()
    user1 = {
        'email':"lucas.hzzheng@gmail.com",
        'password':"lucaszheng",
        'name_first':"",
        'name_last':"Zheng"

    }
    resp = requests.post(f"{url}/auth/register", json=user1)
    assert json.loads(resp.text)['code'] == 400

def test_auth_register_dm(url):
    """test user register with used email"""
    clear()
    reg_user(url)
    user2 = {
        'email':"lucas.hzzheng@gmail.com",
        'password':"lucaszheng",
        'name_first':"Lucas",
        'name_last':  "Zheng"
    }
    resp = requests.post(f"{url}/auth/register", json=user2)
    assert json.loads(resp.text)['code'] == 400
