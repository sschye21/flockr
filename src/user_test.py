'''user tests'''
import pytest
from auth import auth_register, auth_login
from other import clear
from error import InputError
from user import user_profile, user_profile_sethandle

def test_success_user_info():
    """# test for successful return of information"""
    clear()
    register_data = auth_register("michael@gmail.com", "123456", "Michael", "Comino")
    auth_login("michael@gmail.com", "123456")
    token = register_data['token']
    u_id = register_data['u_id']
    user_profile_sethandle(token, "MichaelC")
    profile = user_profile(token, u_id)['user']
    assert profile['u_id'] == u_id

def test_invalid_uid():
    """# test for u_id is not a valid user -- input error"""
    clear()
    register_data = auth_register("michael@gmail.com", "123456", "Michael", "Comino")
    auth_login("michael@gmail.com", "123456")
    token1 = register_data['token']
    with pytest.raises(InputError):
        user_profile(token1, "MC")

def test_change_handle():
    """#test for a successful update of handle"""
    clear()
    register_data = auth_register("michael@gmail.com", "123456", "Michael", "Comino")
    auth_login("michael@gmail.com", "123456")
    token1 = register_data['token']
    u_id1 = register_data['u_id']
    user_profile_sethandle(token1, "MichaelC")
    profile = user_profile(token1, u_id1)['user']
    assert profile['handle_str'] == "MichaelC"

def test_handle_short():
    """#test where handle entered is less than 3 characters"""
    clear()
    register_data = auth_register("michael@gmail.com", "123456", "Michael", "Comino")
    auth_login("michael@gmail.com", "123456")
    token1 = register_data['token']
    with pytest.raises(InputError):
        user_profile_sethandle(token1, "MC")

def test_handle_long():
    """#test where handle entered is more than 20 characters"""
    clear()
    register_data = auth_register("michael@gmail.com", "123456", "Michael", "Comino")
    auth_login("michael@gmail.com", "123456")
    token1 = register_data['token']
    with pytest.raises(InputError):
        user_profile_sethandle(token1, "M"*21)

def test_handle_3():
    """#test where handle entered is 3 characters"""
    clear()
    register_data = auth_register("michael@gmail.com", "123456", "Michael", "Comino")
    auth_login("michael@gmail.com", "123456")
    token1 = register_data['token']
    user_profile_sethandle(token1, "M"*3)

def test_handle_20():
    """#test where handle entered is 20 characters"""
    clear()
    register_data = auth_register("michael@gmail.com", "123456", "Michael", "Comino")
    auth_login("michael@gmail.com", "123456")
    token1 = register_data['token']
    user_profile_sethandle(token1, "M"*20)

def test_invalid_token():
    """#test where user has an invalid token but attempts to change handle"""
    clear()
    auth_register("michael@gmail.com", "123456", "Michael", "Comino")
    token2 = "invalid token"
    with pytest.raises(InputError):
        user_profile_sethandle(token2, "MComino")

def test_handle_taken():
    """#test where user attempts to change handle but another user already has that handle"""
    clear()
    register_data1 = auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    register_data2 = auth_register("michael@gmail.com", "123456", "Michael", "Comino")
    token1 = register_data1['token']
    token2 = register_data2['token']
    user_profile_sethandle(token2, "MichaelC")
    with pytest.raises(InputError):
        user_profile_sethandle(token1, "MichaelC")
