'''this test was written to test the auth.py login function'''
import pytest
from auth import auth_login, auth_register
from error import InputError
from other import clear

def test_login_correct():
    """correct login"""
    clear()
    register_user = auth_register("steven@gmail.com", "123456", "Steven", "Chye")
    login_user = auth_login("steven@gmail.com", "123456")
    assert register_user["u_id"] == login_user["u_id"]

def test_login_wrong_password():
    """test login with wrong password"""
    clear()
    auth_register("michael@gmail.com", "123456", "Steven", "Chye")
    with pytest.raises(InputError):
        auth_login("michael@gmail.com", "password")

def test_login_incorrect_email():
    """test login with incorrect email"""
    clear()
    auth_register("guest@gmail.com", "123456", "Steven", "Chye")
    with pytest.raises(InputError):
        auth_login("brittany@gmail.com", "123456")

def test_no_registration():
    """test login with no registed"""
    clear()
    with pytest.raises(InputError):
        auth_login("sidd.com@gmail", "123456")
