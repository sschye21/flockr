"""tests for auth_register function in auth.py"""
import pytest
from auth import auth_register
from error import InputError
from other import clear

#pylint: disable = C0303
#test for successful registration of user
def test_auth_register(): 
    """test that passes for successful registration of user"""
    clear()
    assert auth_register("lucas.hzzheng@gmail.com", "lucaszheng", "Lucas", "Zheng")

#test invalid email
def test_auth_register_email():
    """test raises InputError due to invalid email entered"""
    clear()
    with pytest.raises(InputError):
        auth_register("lucas.hzzhel.com", "lucaszheng", "Lucas", "Zheng")

#test for invalid password entered
def test_auth_register_password():
    """test raises InputError as password entered is too short"""
    clear()
    with pytest.raises(InputError):
        auth_register("nick.hzzheng@gmail.com", "luca", "Lucas", "Zheng")

#test for invalid firstname      
def test_auth_register_name():
    """test raises InputError as firstname is too short"""
    clear()
    with pytest.raises(InputError):
        auth_register("nick.hzzheng@gmail.com", "lucaszheng", "", "Zheng")

#test for invalid repeated email  
def test_auth_register_repeat_email(): 
    """test raises InputError for repeat email entered"""  
    clear()
    auth_register("nick.hzz@gmail.com", "lucaszheng", "Lucas", "Zheng")
    with pytest.raises(InputError):
        auth_register("nick.hzz@gmail.com", "password", "Guest", "Test")

#test for password too short
def test_auth_register_short_password():
    """test raises InputError as password entered is too short"""
    clear()
    with pytest.raises(InputError):
        auth_register("steven@gmail.com", "a", "Steven", "Chye")

#test invalid lastname entered
def test_auth_register_no_lastname():
    """test raises InputError as lastname entered is too short"""
    clear()
    with pytest.raises(InputError):
        auth_register("steven@gmail.com", "password", "Steven", "")

#test for firstname too big >50 characters
def test_auth_register_firstname_toobig():
    """test raises InputError as firstname is greater than 50 characters"""
    clear()
    with pytest.raises(InputError):
        auth_register("steven@gmail.com", "password", "Steven"*376423, "Chye")

#test for lastname too big
def test_auth_register_firstname_toosmall():
    """test raises InputError as lastname if too big greater than 50"""
    clear()
    with pytest.raises(InputError):
        auth_register("steven@gmail.com", "password", "Steven", "Chye"*6743)

#edge case where first name is 1 character
def test_edge_firstname_1():
    """edge case test where first name is 1 character"""
    clear()
    assert auth_register("steven@gmail.com", "password", "S", "Chye")

#edge case where first name is 50 characters
def test_edge_firstname_50():
    """edge case test where first name is 50 characters"""
    clear()
    assert auth_register("steven@gmail.com", "password", "S"*50, "Chye")

#edge case where last name is 1 character
def test_edge_lastname_1():
    """edge case test where last name is 1 character"""
    clear()
    assert auth_register("steven@gmail.com", "password", "Steven", "C")

#edge case where last name is 50 characters
def test_edge_lastname_50():
    """edge case test where last name is 1 character"""
    clear()
    assert auth_register("steven@gmail.com", "password", "Steven", "C"*50)

#edge case where password is 6 characters
def test_edge_password_6():
    """edge case test where last name is 1 character"""
    clear()
    assert auth_register("steven@gmail.com", "abcdef", "Steven", "Chye")
