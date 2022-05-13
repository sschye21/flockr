'''test for user_profile_uploadphoto in user.py'''
import pytest
from PIL import Image
from auth import auth_register, auth_login
from other import clear
from error import InputError, AccessError
from user import user_profile, user_profile_uploadphoto
from data_stores import auth_datastore
#pylint:disable = C0301
SHREK = "https://img1.looper.com/img/gallery/things-only-adults-notice-in-shrek/intro-1573597941.jpg"
INVALID = "BCVFWEE"
NOT_A_JPG = "https://i.pinimg.com/originals/6e/1a/3c/6e1a3c6621e3d1b576d38a97485dfe79.png"
ERROR = "https://www.youtube.com/fjnekjfnewkjfn"

#def user_profile_uploadphoto(token ,img_url, x_start, y_start, x_end, y_end):
#assumption: profile image max is 0, 0, 500, 500
#test for successful upload and crop of photo
def test_success_upload():
    '''success case where user uploads and crops a photo to correct size'''
    clear()
    auth_store = auth_datastore()
    auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    login_user = auth_login("steven@gmail.com", "123456")
    token1 = login_user['token']
    u_id1 = login_user['u_id']

    for i in auth_store:
        if i['token'] == token1:
            first_name = i['name_first']

    user_profile_uploadphoto(token1, SHREK, 0, 0, 300, 300)
    profile = user_profile(token1, u_id1)
    profile_img_url = profile['user']['profile_img_url']
    image_name = first_name + str(u_id1) + ".jpg"

    assert profile_img_url == ("http://127.0.0.1:5001/" + image_name)
    ##if image is not saved, we can't open the image below
    ##if no error then image is saved successfully
    Image.open("profile_photo.jpg")

#test invalid user
def test_invalid_user():
    'success case where user uploads and crops a photo to correct size'
    clear()
    auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    auth_login("steven@gmail.com", "123456")
    token2 = "hello i am invalid"

    with pytest.raises(AccessError):
        user_profile_uploadphoto(token2, SHREK, 0, 0, 300, 300)

#test photo is invalid http status
def test_photo_invalid_http_status():
    'success case where user uploads and crops a photo to correct size'
    clear()
    auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    login_user = auth_login("steven@gmail.com", "123456")
    token1 = login_user['token']

    with pytest.raises(InputError):
        user_profile_uploadphoto(token1, INVALID, 0, 0, 300, 300)

#test crop dimensions entered is invalid
def test_invalid_bounds():
    'success case where user uploads and crops a photo to correct size'
    clear()
    auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    login_user = auth_login("steven@gmail.com", "123456")
    token1 = login_user['token']

    with pytest.raises(InputError):
        user_profile_uploadphoto(token1, SHREK, 0, 0, 99999, 99999)

#test image is not a jpg
def test_not_a_jpg():
    'success case where user uploads and crops a photo to correct size'
    clear()
    auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    login_user = auth_login("steven@gmail.com", "123456")
    token1 = login_user['token']

    with pytest.raises(InputError):
        user_profile_uploadphoto(token1, NOT_A_JPG, 0, 0, 300, 300)

#test edge case maximum dimesions - see assumptions.md
def test_edge_case_max():
    'success case where user uploads and crops a photo to correct size'
    clear()
    auth_store = auth_datastore()
    auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    login_user = auth_login("steven@gmail.com", "123456")
    token1 = login_user['token']
    u_id1 = login_user['u_id']

    for i in auth_store:
        if i['token'] == token1:
            first_name = i['name_first']

    user_profile_uploadphoto(token1, SHREK, 0, 0, 500, 500)
    profile = user_profile(token1, u_id1)
    profile_img_url = profile['user']['profile_img_url']

    image_name = first_name + str(u_id1) + ".jpg"

    assert profile_img_url == ("http://127.0.0.1:5001/" + image_name)
    ##if image is not saved, we can't open the image below
    ##if no error then image is saved successfully
    Image.open("profile_photo.jpg")

#test case where status code does not return 200
def test_not_return_200():
    'fail case where status code does not return 200 due to an error'
    clear()
    auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    login_user = auth_login("steven@gmail.com", "123456")
    token1 = login_user['token']

    with pytest.raises(InputError):
        user_profile_uploadphoto(token1, ERROR, 0, 0, 300, 300)

#test where photo is not cropped properly
def test_not_cropped_correct():
    'fail case where incorrect dimensions - ie. not a square'
    clear()
    auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    login_user = auth_login("steven@gmail.com", "123456")
    token1 = login_user['token']

    with pytest.raises(InputError):
        user_profile_uploadphoto(token1, ERROR, 0, 10, 30, 20)
