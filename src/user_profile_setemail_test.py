"""this test will test the user_profile_setemail function within user.py"""

import pytest
from auth import auth_register, auth_login
from other import clear
from error import InputError, AccessError
from user import user_profile, user_profile_setemail

#test for a successful update of email address
def test_change_email():
    "test for successful update of users' email"
    clear()
    register_data = auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    auth_login("steven@gmail.com", "123456")
    token1 = register_data['token']
    u_id1 = register_data['u_id']

    user_profile_setemail(token1, "david@gmail.com")
    profile = user_profile(token1, u_id1)['user']

    assert profile['email'] == "david@gmail.com"

#test where user attempts to change email address but it is already taken
def test_email_taken():
    """test where email is already taken, raising InputError"""
    clear()
    register_data1 = auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    auth_register("james@gmail.com", "password", "James", "Chye")
    token1 = register_data1['token']

    with pytest.raises(InputError):
        user_profile_setemail(token1, "james@gmail.com")

#test where email entered is not of valid form as provided in spec
def test_email_invalid_form():
    """test where email is in incorrect form as per spec, raising InputError"""
    clear()
    register_data = auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    token1 = register_data['token']

    with pytest.raises(InputError):
        user_profile_setemail(token1, "james.com")

#test where user has an invalid token but attempts to change email
def test_invalid_token():
    """test where user has an invalid token, raising AccessError"""
    clear()
    auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    token2 = "invalid token"

    with pytest.raises(AccessError):
        user_profile_setemail(token2, "hello@gmail.com")

#test where user attempts to change email to same email - see assumptions.md
def test_same_email():
    """raises inputError when user tries to change email to same email as per assumptions.md"""
    clear()
    register_data = auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    auth_login("steven@gmail.com", "123456")
    token1 = register_data['token']

    with pytest.raises(InputError):
        user_profile_setemail(token1, "steven@gmail.com")
