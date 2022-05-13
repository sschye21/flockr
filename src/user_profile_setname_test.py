"""this test was written to test the user_profile_setname function"""

import pytest
from user import user_profile, user_profile_setname
from auth import auth_register, auth_login
from other import clear
from error import InputError, AccessError

#test that will change the first and last name of the user
def test_change_name():
    """test the successful updating of an authorised users' first and last name"""
    clear()
    register_data = auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    auth_login("steven@gmail.com", "123456")

    token1 = register_data['token']
    u_id1 = register_data['u_id']
    user_profile_setname(token1, "Nevets", "Eyhc")
    profile = user_profile(token1, u_id1)['user']
    handle_str = profile['handle_str']

    assert profile['name_first'] == "Nevets"
    assert profile['name_last'] == "Eyhc"
    assert profile['handle_str'] == handle_str

#test that will only change the first name
def test_change_first():
    """this will only change the users' first name"""
    clear()
    register_data = auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    auth_login("steven@gmail.com", "123456")

    token1 = register_data['token']
    u_id1 = register_data['u_id']
    user_profile_setname(token1, "Nevets", "Chye")
    profile = user_profile(token1, u_id1)['user']
    handle_str = profile['handle_str']

    assert profile['name_first'] == "Nevets"
    assert profile['name_last'] == "Chye"
    assert profile['handle_str'] == handle_str

#test that will only change the last name
def test_change_last():
    """this test will only change the users' last name"""
    clear()
    register_data = auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    auth_login("steven@gmail.com", "123456")

    token1 = register_data['token']
    u_id1 = register_data['u_id']
    user_profile_setname(token1, "Steven", "Eyhc")
    profile = user_profile(token1, u_id1)['user']
    handle_str = profile['handle_str']

    assert profile['name_first'] == "Steven"
    assert profile['name_last'] == "Eyhc"
    assert profile['handle_str'] == handle_str

#test where user with an invalid token tries to change name
def test_invalid_token():
    """User with an invalid token, raising InputError"""
    clear()
    auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    auth_login("steven@gmail.com", "123456")
    token2 = "invalid token"

    with pytest.raises(AccessError):
        user_profile_setname(token2, "Steven", "Chye")

#test case where the first name entered is greater than 50 characters
def test_firstname_long():
    """test where first name is >50 characters, raising InputError"""
    clear()
    register_data = auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    auth_login("steven@gmail.com", "123456")
    token1 = register_data['token']
    with pytest.raises(InputError):
        user_profile_setname(token1, "S"*23874, "Chye")

#test case where the firstname is shorter than 1 character
def test_firstname_short():
    """test where firstname is <1 character, raising InputError"""
    clear()
    register_data = auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    auth_login("steven@gmail.com", "123456")
    token1 = register_data['token']
    with pytest.raises(InputError):
        user_profile_setname(token1, "", "Chye")

#test case where the lastname is greater than 50 characters
def test_lastname_long():
    """test where last name is >50 characters, raising InputError"""
    clear()
    register_data = auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    auth_login("steven@gmail.com", "123456")
    token1 = register_data['token']
    with pytest.raises(InputError):
        user_profile_setname(token1, "Steven", "C"*384567872)

#test case where the lastname is shorter than 1 character
def test_lastname_short():
    """test where last name is <1 character, raising InputError"""
    clear()
    register_data = auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    auth_login("steven@gmail.com", "123456")
    token1 = register_data['token']
    with pytest.raises(InputError):
        user_profile_setname(token1, "Steven", "")

#edge case testing for firstname where it is the minimum character limit
def test_edge_firstname1():
    """edge case test, minimum character limit of 1 for firstname"""
    clear()
    register_data = auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    auth_login("steven@gmail.com", "123456")

    token1 = register_data['token']
    u_id1 = register_data['u_id']
    user_profile_setname(token1, "S", "Chye")
    profile = user_profile(token1, u_id1)['user']
    handle_str = profile['handle_str']

    assert profile['name_first'] == "S"
    assert profile['name_last'] == "Chye"
    assert profile['handle_str'] == handle_str
#edge case testing for firstname where it is the maximum character limit
def test_edge_firstname50():
    """edge case testing maximum character limit of 50 for firstname"""
    clear()
    register_data = auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    auth_login("steven@gmail.com", "123456")

    token1 = register_data['token']
    u_id1 = register_data['u_id']
    user_profile_setname(token1, "S"*50, "Chye")
    profile = user_profile(token1, u_id1)['user']
    #saves me from typing 50 characters
    handle_str = profile['handle_str']

    assert profile['name_first'] == "S"*50
    assert profile['name_last'] == "Chye"
    assert profile['handle_str'] == handle_str

#edge case testing for lastname where it is the minimum character limit
def test_edge_lastname1():
    """edge case test for lastname mimnimum character limit of 1"""
    clear()
    register_data = auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    auth_login("steven@gmail.com", "123456")

    token1 = register_data['token']
    u_id1 = register_data['u_id']
    user_profile_setname(token1, "Steven", "C")
    profile = user_profile(token1, u_id1)['user']
    handle_str = profile['handle_str']

    assert profile['name_first'] == "Steven"
    assert profile['name_last'] == "C"
    assert profile['handle_str'] == handle_str

#edge case testing for lastname where it is the maximum character limit
def test_edge_lastname50():
    """edge case test for last name maximum character limit of 50 for lastname"""
    clear()
    register_data = auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    auth_login("steven@gmail.com", "123456")

    token1 = register_data['token']
    u_id1 = register_data['u_id']
    user_profile_setname(token1, "Steven", "C"*50)
    profile = user_profile(token1, u_id1)['user']
    #saves me from typing 50 characters
    handle_str = profile['handle_str']

    assert profile['name_first'] == "Steven"
    assert profile['name_last'] == "C"*50
    assert profile['handle_str'] == handle_str
