'''auth_register auth_login auth_logout functions'''
import re
import random
import hashlib
import smtplib
import string
from error import InputError, AccessError
from data_stores import auth_datastore, resetcode_datastore
users = dict()
EMAIL = "slakrs1531@gmail.com"
PASSWORD = "1531python"

REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
def token_generator(u_id):
    """generate a hash token based on u_id"""
    return hashlib.sha256(str(u_id).encode()).hexdigest()

def check_repeat_email(email):
    """check if email is used by others"""
    auth_store = auth_datastore()
    repeat = False
    for i in auth_store:
        if i['email'] == email:
            repeat = True
    return repeat

def check_repeat_u_id(u_id):
    """check if u_id is used by others"""
    auth_store = auth_datastore()
    repeat = False
    for i in auth_store:
        if i['u_id'] == u_id:
            repeat = True
    return repeat

def check_valid_email(email):
    """check if email is in valid format"""
    if re.search(REGEX, email):
        return False
    return True

def logout_token(token):
    """check if token can be delete from datastore"""
    token_data = auth_datastore()

    try:
        del token_data[token]
        return True
    except KeyError:
        return False

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    'id generator for reset code'''
    return ''.join(random.choice(chars) for _ in range(size))


def get_user(field, request):
    'get user'
    auth_store = auth_datastore()
    for i in auth_store:
        if i[str(field)] == request:
            return i
    return {}

# AUTH_LOGIN
# Given a registered user's email and password and generates a valid
# token for the user to remain authenticated.
def auth_login(email, password):
    """user login functions"""
    #test if email is invalid --> raise InputError
    if check_valid_email(email):
        raise InputError(description="Invalid Email")
    #grab the users data
    auth_store = auth_datastore()
    for i in auth_store:
        if i['email'] == email:
            if i['password'] == password:
                return {
                    'u_id': i['u_id'],
                    'token': i['token']
                }
            raise InputError(description="Password entered is incorrect")

    raise InputError("Email does not exist")

# AUTH_LOGOUT
# Given an active token, invalidates the token to log the user out.
def auth_logout(token):
    """user logout functions"""
    auth_data = auth_datastore()

    for j in auth_data:
        if not j['token'] == token:
            raise AccessError(description="Unsuccessful Logout, Invalid Token")

    for i in auth_data:
        if i['token'] == token:
            return {
                'is_success': True,
            }
            #if an invalid token is given, the logout fails
    return{
        'is_success': False
    }

def auth_register(email, password, name_first, name_last):
    """user register functions"""
    auth_store = auth_datastore()
    user = {}

    if not re.search(REGEX, email):
        raise InputError(description="Please Enter a valid email")
    if check_repeat_email(email):
        raise InputError(description="Email has been used")
    if len(password) < 6:
        raise InputError(description="Please make a complex password")
    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError(description="Please Enter a valid name")
    if len(name_last) < 1 or len(name_last) > 50:
        # Users do not have a middle name.
        raise InputError(description="Please Enter a valid name")
    name = name_first + name_last
    name = name.lower()
    name = name[:21]
    u_id = random.randint(1, 1000)
    while check_repeat_u_id(u_id):
        # Number of users does not exceed 1000.
        u_id = random.randint(1, 1000)
    token = token_generator(u_id)
    user = {
                'u_id': u_id,
                'name_first': name_first,
                'name_last': name_last,
                'email': email,
                'handle_str': name,
                'token': token,
                'password': password,
                'permission_id': 2,
                'profile_img_url': None,
    }
    auth_store.append(user)
    auth_store[0]['permission_id'] = 1
    return {
        'u_id': u_id,
        'token': token,
    }

def auth_passwordreset_request(email):
    'send a request for user to reset password'
    reset_store = resetcode_datastore()
    auth_store = auth_datastore()
    user_request = {}
    match = 0

    for i in auth_store:
        if i['email'] == email:
            match = 1

            code = id_generator()

            user_request = {
                'email': email,
                'reset_code': code,
            }

            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(EMAIL, PASSWORD)
            server.sendmail(
                EMAIL,
                email,
                code)
            server.quit()

    reset_store.append(user_request)

    if match == 0:
        raise InputError(description="Email entered does not belong to a user")

def auth_passwordreset_reset(reset_code, new_password):
    'reset password'
    reset_store = resetcode_datastore()
    find = False
    for i in reset_store:
        if i['reset_code'] == reset_code:
            find = True
            email = i['email']
            user = get_user('email', email)
            if len(new_password) > 6:
                user['password'] = new_password

            else:
                raise InputError(description="Password is short")

    if not find:
        raise InputError(description="Incorrect reset code")
    return {}
