'''test written for auth_logout function within auth.py'''
import pytest
from auth import auth_login, auth_logout, auth_register
from error import AccessError
from other import clear


def test_logout_success():
    """#logout is successful"""
    clear()
    auth_register("guest123@gmail.com", "123456", "John", "Smith")
    login = auth_login("guest123@gmail.com", "123456")
    token = login['token']
    logout = auth_logout(token)
    assert logout['is_success']

def test_logout_failed():
    """invalid token"""
    token = "invalid_token"
    with pytest.raises(AccessError):
        auth_logout(token)
