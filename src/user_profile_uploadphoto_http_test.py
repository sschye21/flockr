'''user_profile_http functions http tests'''
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import json
import requests
import pytest
from other import clear
from system_helper_functions import reg_user

#pylint: disable = C0301
SHREK = "https://img1.looper.com/img/gallery/things-only-adults-notice-in-shrek/intro-1573597941.jpg"
INVALID = "BCVFWEE"
NOT_A_JPG = "https://i.pinimg.com/originals/6e/1a/3c/6e1a3c6621e3d1b576d38a97485dfe79.png"
ERROR = "https://www.youtube.com/fjnekjfnewkjfn"

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
#test where successful upload of profile photo
def test_successful_upload(url):
    '''success case where user successfully updates profile picture'''
    clear()
    user1 = reg_user(url)[0]
    first_name = user1['name_first']
    print(user1['profile_img_url'])
    image_name = first_name + str(user1['u_id']) + ".jpg"
    upload = {
        'token': user1['token'],
        'img_url': SHREK,
        'x_start': 0,
        'y_start': 0,
        'x_end': 300,
        'y_end': 300
    }
    requests.post(url + "/user/profile/uploadphoto", json=upload)
    check = {
        'token':user1['token'],
        'u_id':user1['u_id']
    }
    resp_c = requests.get(url + "user/user_profile", params=check)
    result = json.loads(resp_c.text)['user']
    assert result['profile_img_url'] == ("http://127.0.0.1:5001/" + image_name)

#test where user is invalid
def test_invalid_user(url):
    '''400 error as user is invalid'''
    clear()
    reg_user(url)
    user2 = 123
    upload = {
        'token': user2,
        'img_url': SHREK,
        'x_start': 0,
        'y_start': 0,
        'x_end': 300,
        'y_end': 300
    }
    resp = requests.post(url + "/user/profile/uploadphoto", json=upload)
    result = json.loads(resp.text)
    assert result['code'] == 400

#test where image is not a jpg
def test_not_a_jpg(url):
    '''400 error as image is not a jpg'''
    clear()
    user1 = reg_user(url)[0]
    upload = {
        'token': user1['token'],
        'img_url': NOT_A_JPG,
        'x_start': 0,
        'y_start': 0,
        'x_end': 300,
        'y_end': 300
    }
    resp = requests.post(url + "/user/profile/uploadphoto", json=upload)
    result = json.loads(resp.text)
    assert result['code'] == 400

#test where url link is invalid
def test_error_page(url):
    '''400 error as url link provided is invalid'''
    clear()
    user1 = reg_user(url)[0]
    upload = {
        'token': user1['token'],
        'img_url': INVALID,
        'x_start': 0,
        'y_start': 0,
        'x_end': 300,
        'y_end': 300
    }
    resp = requests.post(url + "/user/profile/uploadphoto", json=upload)
    result = json.loads(resp.text)
    assert result['code'] == 400

#test where user enters invalid bounds
def test_invalid_bounds(url):
    '''400 error as user enters invalid bounds'''
    clear()
    user1 = reg_user(url)[0]
    upload = {
        'token': user1['token'],
        'img_url': SHREK,
        'x_start': -999,
        'y_start': -999,
        'x_end': 99999,
        'y_end': 99999
    }
    resp = requests.post(url + "/user/profile/uploadphoto", json=upload)
    result = json.loads(resp.text)
    assert result['code'] == 400

#test where img_url is not 200
def test_not_200(url):
    '''400 error as user enters error img_url'''
    clear()
    user1 = reg_user(url)[0]
    upload = {
        'token': user1['token'],
        'img_url': ERROR,
        'x_start': 0,
        'y_start': 0,
        'x_end': 300,
        'y_end': 300
    }
    resp = requests.post(url + "/user/profile/uploadphoto", json=upload)
    result = json.loads(resp.text)
    assert result['code'] == 400
