'''password reset tests'''
import pytest
from auth import auth_register, auth_passwordreset_request, auth_passwordreset_reset, id_generator
from data_stores import resetcode_datastore, auth_datastore
from error import InputError
from other import clear

#pylint: disable = C0303
#############################################################
#                   PASSWORDRESET_REQUEST                   #
#############################################################
def test_passwordreset_request():
    '''successful password reset request'''
    clear()
    auth_register("guest123@gmail.com", '123Asdf', "John", "Smith")

    auth_passwordreset_request('guest123@gmail.com')

    reset_store = resetcode_datastore()
    auth_store = auth_datastore()

    email_match = 0

    for i in auth_store:
        if i['email'] == 'guest123@gmail.com':
            email_match = 1
    assert email_match == 1   

    flag = 0
    for i in reset_store:
        if i['email'] == 'guest123@gmail.com':
            flag = 1
    assert flag == 1

#############################################################
#                   PASSWORDRESET_RESET                     #
#############################################################
def test_passwordreset_reset():
    '''successful password reset'''
    clear()
    reset_store = resetcode_datastore()

    auth_register("guest123@gmail.com", "123456", "Steven", "Chye")

    auth_passwordreset_request('guest123@gmail.com')

    for i in reset_store:
        if i['email'] == "guest123@gmail.com":
            reset_code = i['reset_code']

    auth_passwordreset_reset(reset_code, "newpassword")

    auth_store = auth_datastore()

    check = False

    for i in auth_store:
        if i['password'] == "newpassword":
            check = True

    assert check

#test incorrect reset code
def test_wrongresetcode():
    '''fail case where reset code is invalid'''
    clear()
    resetcode_datastore()

    auth_register("guest123@gmail.com", '123Asdf', "John", "Smith")

    auth_passwordreset_request('guest123@gmail.com')

    with pytest.raises(InputError):
        auth_passwordreset_reset('abcd', 'newpassword')

#test where password is invalid
def test_invalidpassword():
    '''fail case where password entered is invalid'''
    clear()
    resetcode_datastore()

    auth_register("guest123@gmail.com", '123Asdf', "John", "Smith")
    code = id_generator()
    auth_passwordreset_request('guest123@gmail.com')

    with pytest.raises(InputError):
        auth_passwordreset_reset(code, 's')
