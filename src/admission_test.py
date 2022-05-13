"""tests for admin_userpermission_change from other.py"""
import pytest
from error import InputError, AccessError
from auth import auth_register, auth_login
from channels import channels_create
from channel import channel_details, channel_invite
from other import admin_userpermission_change, clear
######################################
#   ADMIN_USERPERMISSION_CHANGE_TEST #
######################################

# admin_userpermission_change(token, u_id, permission_id)
# if permission_id = 1 --> owner - like privileges
# if permission_id = 2 --> member
#pylint: disable = C0303
def test_userpermission_change():
    """test normal userpermission_change"""
    result = auth_register("b.li@gmail.com", "password", "brittany", "li")
    auth_login("b.li@gmail.com", "password")
    token = result['token']
    u_id = result['u_id']

    channel_id = channels_create(token, 'Mango', True)
    

    result2 = auth_register("a.ci@gmail.com", "password", "steve", "chye")
    auth_login("a.ci@gmail.com", "password")
    u_id2 = result2['u_id']
    channel_invite(token, channel_id, u_id2)

    admin_userpermission_change(token, u_id2, 1)
    result3 = channel_details(token, channel_id)
    assert result3['owner_members'] == [
        {'name_first': 'brittany',
         'name_last': 'li',
         'u_id': u_id},
        {'name_first': 'steve',
         'name_last': 'chye',
         'u_id': u_id2}
    ]

#test where user has invalid permissions
def test_invalid_permission():
    """test raises InputError as user has invalid permission_id"""
    clear()
    result = auth_register("b.li@gmail.com", "password", "brittany", "li")
    auth_login("b.li@gmail.com", "password")
    token = result['token']

    result2 = auth_register("a.ci@gmail.com", "password", "steve", "chye")
    auth_login("a.ci@gmail.com", "password")
    u_id2 = result2['u_id']

    with pytest.raises(InputError):
        admin_userpermission_change(token, u_id2, 3)

#test where user has an invalid u_id
def test_invalid_uid():
    """test raises InputError as user has an invalid u_id"""
    clear()
    result = auth_register("b.li@gmail.com", "password", "brittany", "li")
    auth_login("b.li@gmail.com", "password")
    token = result['token']

    auth_register("a.ci@gmail.com", "password", "steve", "chye")
    auth_login("a.ci@gmail.com", "password")

    with pytest.raises(InputError):
        admin_userpermission_change(token, '123456', 1)

#test where user is not an owner
def test_not_an_owner():
    """test that raises AccessError as user is not an owner"""
    clear()
    auth_register("b.li@gmail.com", "password", "brittany", "li")
    result2 = auth_register("a.ci@gmail.com", "password", "steve", "chye")
    u_id2 = result2['u_id']

    result3 = auth_register("b.ci@gmail.com", "password", "pteve", "hhye")
    token3 = result3['token']

    with pytest.raises(AccessError):
        admin_userpermission_change(token3, u_id2, 1)
