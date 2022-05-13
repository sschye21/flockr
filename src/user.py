'''user functions'''
import re
import os
import urllib
import requests
from PIL import Image
from error import InputError, AccessError
from data_stores import auth_datastore
from auth import check_repeat_u_id, check_repeat_email
from channel import token_to_u_id
#pylint: disable = C0301
#pylint: disable = R0913
#pylint: disable = R0914
REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

def user_profile(token, u_id):
    """view user_profile"""
    auth_store = auth_datastore()
    user_id = token_to_u_id(token)
    if not user_id == u_id:
        raise InputError(description="token not match with u_id")
    if not check_repeat_u_id(u_id):
        raise InputError(description="u_id is invalid")
    for element in auth_store:
        if element['u_id'] == u_id:
            user_details = {
                'u_id': element['u_id'],
                'email': element['email'],
                'name_first': element['name_first'],
                'name_last': element['name_last'],
                'handle_str': element['handle_str'],
                'profile_img_url': element['profile_img_url'],
            }
            #user.append(user_details)
            break
    return {'user': user_details}

# Update the authorised user's handle (i.e. display name)
def user_profile_sethandle(token, handle_str):
    """change handle for user"""
    auth_data = auth_datastore()
    user_id = token_to_u_id(token)
    found = False
    for user in auth_data:
        if not user['token'] == token and user['handle_str'] == handle_str:
            raise InputError(description="Handle has already been taken")

    for i in auth_data:
        if i['token'] == token and i['u_id'] == user_id:
            found = True
            i['handle_str'] = handle_str
            if len(handle_str) < 3:
                raise InputError(description="Handle is less than 3 characters")
            if len(handle_str) > 20:
                raise InputError(description="Handle is greater than 20 characters")
            break
    if not found:
        raise InputError(description="Invalid")
    return{}

def user_profile_setname(token, name_first, name_last):
    """set names"""
    auth_data = auth_datastore()
    user_id = token_to_u_id(token)
    for i in auth_data:
        #check if token and u_id is valid
        if i['token'] == token and i['u_id'] == user_id:
            i['name_first'] = name_first
            if len(name_first) < 1:
                raise InputError(description="First name is less than the minimum of 1 character")
            if len(name_first) > 50:
                raise InputError(description="First name is greater than the maximum of 50 characters")
            i['name_last'] = name_last
            if len(name_last) < 1:
                raise InputError(description="Last name is less than the minimum of 1 character")
            if len(name_last) > 50:
                raise InputError(description="Last name is greater than the maximum of 50 characters")
        else:
            raise AccessError(description="Invalid Token")
    return {}

#update the users email when the function is called
def user_profile_setemail(token, email):
    """change email"""
    auth_data = auth_datastore()
    #check if email change is in correct format
    if not re.search(REGEX, email):
        raise InputError(description="Please Enter a valid email")

    #email has already been taken
    if check_repeat_email(email):
        raise InputError(description="Email Address has already been taken")
    #if email has not been taken, update the email address
    token_valid = False
    for i in auth_data:
        if i['token'] == token:
            token_valid = True
            i['email'] = email
    if not token_valid:
        raise AccessError(description="Invalid Token")

    return {}
#pylint: disable = R0912
#upload_photo function
def user_profile_uploadphoto(token, img_url, x_start, y_start, x_end, y_end):
    '''uploading a profile picture'''
    auth_store = auth_datastore()
    #check if boundaries are invalid
    if x_start < 0 or x_start > 0:
        raise InputError(description="X position must be 0")
    if y_start < 0 or y_start > 0:
        raise InputError(description="Y position must be 0")
    if x_end < 0 or x_end > 500:
        raise InputError(description="Invalid bounds")
    if y_end < 0 or y_end > 500:
        raise InputError(description="Invalid bounds")

    #check if token is valid
    token_valid = False
    for i in auth_store:
        if i['token'] == token:
            token_valid = True
            first_name = i['name_first']
            u_id = i['u_id']
    if not token_valid:
        raise AccessError(description="Invalid Token")

    #check if image is a valid image
    try:
        img = requests.get(img_url)
    except:
        raise InputError(description="Not a valid url")

    if not img.status_code == 200:
        raise InputError(description="Expected status code 200, but got {img.status_code}")

    img_formats = ("image/jpg", "image/jpeg")
    head = requests.head(img_url)
    if not head.headers["content-type"] in img_formats:
        raise InputError("Not a jpg")

    urllib.request.urlretrieve(img_url, "profile_photo.jpg")
    image = Image.open("profile_photo.jpg")
    cropped = image.crop((x_start, y_start, x_end, y_end))
    file_path = str(os.getcwd()) + "/images"
    if not os.path.exists(file_path):
        os.mkdir(file_path)
    image_name = first_name + str(u_id) + ".jpg"
    file_path = file_path + "/" + image_name
    cropped.save(file_path)

    url = urllib.parse.urljoin("http://127.0.0.1:5001/", image_name)

    for element in auth_store:
        if element['token'] == token:
            element['profile_img_url'] = url
    return {}
