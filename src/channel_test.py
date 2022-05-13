'''channel tests file'''
import pytest
from channels import channels_create
from error import InputError, AccessError
from auth import auth_register
#pylint:disable=C0301
from channel import channel_removeowner, channel_addowner, channel_leave, channel_join, channel_details, channel_invite
from other import clear

##################
# CHANNEL_INVITE #
##################
def test_channel_invite():
    """test normal invite"""
    result = auth_register("lucas.hzzheng@gamil.com", "lucaszheng", "Lucas", "Zheng")
    token = result['token']
    channel_id = channels_create(token, 'Room 28', True)
    invited = auth_register("nick.hzzheng@gamil.com", "lucaszheng", "Nick", "Zheng")
    u_id = invited['u_id']
    channel_invite(token, channel_id, u_id)
    result2 = channel_details(token, channel_id)
    assert result2['all_members'] == [
        {'u_id': u_id, 'name_first': 'Nick', 'name_last': 'Zheng'}
    ]
    clear()

def test_channel_invite_channel_id():
    """test with  invalid channnel_id"""
    result = auth_register("lucas.hzzheng@gamil.com", "lucaszheng", "Lucas", "Zheng")
    token = result['token']
    invited = auth_register("nick.hzzheng@gamil.com", "lucaszheng", "Nick", "Zheng")
    u_id = invited['u_id']
    with pytest.raises(InputError):
        channel_invite(token, 123, u_id)
    clear()

def test_channel_invite_u_id():
    """test with invalid u_id"""
    result = auth_register("lucas.hzzheng@gamil.com", "lucaszheng", "Lucas", "Zheng")
    token = result['token']
    channel_id = channels_create(token, 'Room 28', True)
    with pytest.raises(InputError):
        channel_invite(token, channel_id, 123)
    clear()

def test_channel_invite_not_auth():
    """test with invalid token"""
    result = auth_register("lucas.hzzheng@gamil.com", "lucaszheng", "Lucas", "Zheng")
    token = result['token']
    channel_id = channels_create(token, 'Room 28', True)
    invited = auth_register("nick.hzzheng@gamil.com", "lucaszheng", "Nick", "Zheng")
    u_id = invited['u_id']
    token_invited = invited['token']
    with pytest.raises(AccessError):
        channel_invite(token_invited, channel_id, u_id)
    clear()

###################
# CHANNEL_DETAILS #
###################

def test_channel_details():
    """normal channel details"""
    result = auth_register("shutian@gmil.com", "lucaszheng", "Lucas", "Zheng")
    token = result['token']
    u_id = result['u_id']
    channel_id = channels_create(token, 'Room 28', True)
    result = channel_details(token, channel_id)
    assert result['owner_members'] == [
        {'u_id': u_id, 'name_first': 'Lucas', 'name_last': 'Zheng'}
    ]
    clear()

def test_channel_details_with_invited():
    """test with invited case"""
    result = auth_register("shusstian@gmil.com", "lucaszheng", "Lucas", "Zheng")
    token = result['token']
    channel_id = channels_create(token, 'Room 28', True)
    invited = auth_register("nick.hzz123@gamil.com", "lucaszheng", "Nick", "Zheng")
    u_id = invited['u_id']
    channel_invite(token, channel_id, u_id)
    result1 = channel_details(token, channel_id)
    result2 = channel_details(invited['token'], channel_id)
    assert result1 == result2
    clear()

def test_channel_details_channel_id():
    """test with invalid channel_id"""
    result = auth_register("lucas.hzzheng@gaml.com", "lucaszheng", "Lucas", "Zheng")
    token = result['token']
    with pytest.raises(InputError):
        result = channel_details(token, 123)
    clear()

def test_channel_details_not_auth():
    """test with invalid token"""
    result = auth_register("lcas.hzzheng@gamil.com", "lucaszheng", "Lucas", "Zheng")
    token = result['token']
    channel_id = channels_create(token, 'Room 28', True)
    nick = auth_register("nck.hzzheng@gamil.com", "lucaszheng", "Nick", "Zheng")
    token_nick = nick['token']
    with pytest.raises(AccessError):
        result = channel_details(token_nick, channel_id)
    clear()

#################
# CHANNEL_LEAVE #
#################
################################################################################################
# Given a channel ID, the user removed as a member of this channel
################################################################################################

# assumptions:
    # that the person trying to leave has not already left the channel

# if user is trying to leave a channel they are not apart of
def test_not_channel_member():
    """test not channel_member"""
    result = auth_register("guest1234@gmail.com", '123Asdf', "John", "Smith")
    token = result['token']
    channel1 = channels_create(token, 'Thurs09Mango', True)
    result2 = auth_register("other1@gmail.com", 'Password1', "Sam", "John")
    token2 = result2['token']

    with pytest.raises(AccessError):
        channel_leave(token2, channel1)
    clear()


def test_invalidid_leave():
    """# if channel_ID does not exist"""
    result = auth_register("guest1235@gmail.com", '123Asdf', "John", "Smith")
    token = result['token']
    channel1 = channels_create(token, 'Thurs09Mango', True)
    channel_leave(token, channel1)
    with pytest.raises(InputError):
        channel_leave(token, 123)
    clear()

def test_valid_leave():
    """ if current_ID exists and user is authorised to leave"""
    result = auth_register("guest1236@gmail.com", '123Asdf', "John", "Smith")
    token = result['token']
    channel1 = channels_create(token, 'Thurs09Mango', True)
    channel_leave(token, channel1)
    result2 = channel_details(token, channel1)
    assert result2['all_members'] == []
    clear()
################
# CHANNEL_JOIN #
################
################################################################################################
# Given a channel_id of a channel that the authorised user can join, adds them to that channel
################################################################################################

# assumptions:
    # that the person trying to join is not already a member of the channel


def test_unauthorised():
    """# if user is unauthorised to join channel"""
    result = auth_register("guest1237@gmail.com", '123Asdf', "John", "Smith")
    token = result['token']
    channel1 = channels_create(token, 'Thurs09Mango', False)
    result2 = auth_register("other2@gmail.com", 'Password1', "Sam", "John")
    token2 = result2['token']
    with pytest.raises(AccessError):
        channel_join(token2, channel1)
    clear()

def test_invalidid_join():
    """# if channel_ID does not exist """
    result = auth_register("guest1238@gmail.com", '123Asdf', "John", "Smith")
    token = result['token']
    channel1 = channels_create(token, 'Thurs09Mango', True)
    channel_join(token, channel1)
    with pytest.raises(InputError):
        channel_join(token, 123)
    clear()

def test_valid_join():
    """# if current_ID exists and user is authorised """
    # assuming owner
    result = auth_register("guest1239@gmail.com", '123Asdf', "John", "Smith")
    token = result['token']
    # assuming new user
    result2 = auth_register("other8@gmail.com", 'Password', "Sam", "John")
    token2 = result2['token']
    u_id2 = result2['u_id']
    channel1 = channels_create(token, 'Thurs09Mango', True)
    channel_join(token2, channel1)
    result3 = channel_details(token, channel1)
    assert result3['all_members'] == [
        {'u_id': u_id2, 'name_first': 'Sam', 'name_last': 'John'}
    ]
    clear()
#############
# ADD_OWNER #
#############

def test_make_owner():
    """# Register two users."""
    # Register first user
    result = auth_register('hello@gmail.com', '123456', 'Bob', 'Hi')
    token = result['token']
    u_id = result['u_id']
    # Register second user
    result2 = auth_register('bye@gmail.com', '456789', 'Sam', 'Low')
    token2 = result2['token']
    u_id2 = result2['u_id']
    # Create a channel
    channel_id = channels_create(token, 'Mango', True)
    # Bob automatically becomes owner as he created the channel
    # Sam joins the channel and becomes member
    channel_join(token2, channel_id)
    # Promote Sam to become owner of the same channel
    channel_addowner(token, channel_id, u_id2)
    # Check to see if Sam has become owner
    result3 = channel_details(token, channel_id)
    assert result3['owner_members'] == [
        {'u_id': u_id, 'name_first': 'Bob', 'name_last': 'Hi'},
        {'u_id': u_id2, 'name_first': 'Sam', 'name_last': 'Low'}
    ]
    clear()

def test_invalid_id():
    """# Channel ID is not valid."""
    # Register first user who does not create a channel
    result = auth_register('hello@gmail.com', '123456', 'Bob', 'Hi')
    token = result['token']
    # Register second user
    result2 = auth_register('bye@gmail.com', '456789', 'Sam', 'Low')
    u_id2 = result2['u_id']
    # Channel_addowner function is called but there is no channel_id yet
    # First user attempts to add owner
    with pytest.raises(InputError):
        channel_addowner(token, '123456', u_id2)
    clear()

def test_already_owner():
    """# User is already owner of this channel. """
    # Register user
    result = auth_register('hello@gmail.com', '123456', 'Bob', 'Hi')
    token = result['token']
    u_id = result['u_id']
    # Creates a channel and Bob automatically becomes owner
    channel_id = channels_create(token, 'Mango', True)
    with pytest.raises(InputError):
        channel_addowner(token, channel_id, u_id)
    clear()

def test_invalid_token_add():
    """# Token is invalid. """
    result = auth_register('hello@gmail.com', '123456', 'Bob', 'Hi')
    u_id = result['u_id']
    token = result['token']
    channel_id = channels_create(token, 'Mango', True)
    with pytest.raises(AccessError):
        channel_addowner('hihihihi', channel_id, u_id)
    clear()
################
# REMOVE_OWNER #
################


def test_remove_owner():
    """# Remove an owner in which they revert back to being a member."""
    # Register first user
    result = auth_register('hello@gmail.com', '123456', 'Bob', 'Hi')
    u_id = result['u_id']
    token = result['token']
    # Register second user
    result2 = auth_register('bye@gmail.com', '456789', 'Sam', 'Low')
    token2 = result2['token']
    u_id2 = result2['u_id']
    # Create a channel
    channel_id = channels_create(token, 'Mango', True)
    # Bob automatically becomes owner as he created the channel
    # Sam joins the channel and becomes member
    channel_join(token2, channel_id)
    # Promote Sam to become owner of the same channel
    channel_addowner(token, channel_id, u_id2)
    # Bob removes Sam from being owner of the same channel
    channel_removeowner(token, channel_id, u_id2)
    # Check to see if Sam is still owner
    result3 = channel_details(token, channel_id)
    assert result3['owner_members'] == [
        {'u_id': u_id, 'name_first': 'Bob', 'name_last': 'Hi'}
    ]
    clear()

def test_invalid_id_remove():
    """# Not a valid channel_id."""
    # Register first user who does not create a channel
    result = auth_register('hello@gmail.com', '123456', 'Bob', 'Hi')
    token = result['token']
    # Register second user
    result2 = auth_register('bye@gmail.com', '456789', 'Sam', 'Low')
    u_id2 = result2['u_id']
    # Channel_removeowner function is called but there is no channel_id yet
    # First user attempts to remove owner
    with pytest.raises(InputError):
        channel_removeowner(token, '123456', u_id2)
    clear()

def test_remove_not_owner():
    """# User with user id is not an owner of the channel."""
    # Register first user
    result = auth_register('hello@gmail.com', '123456', 'Bob', 'Hi')
    token = result['token']
    # Register second user
    result2 = auth_register('bye@gmail.com', '456789', 'Sam', 'Low')
    token2 = result2['token']
    u_id2 = result2['u_id']
    # Creates a channel and Bob automatically becomes owner
    channel_id = channels_create(token, 'Mango', True)
    # Sam joins the channel as member
    channel_join(token2, channel_id)
    with pytest.raises(InputError):
        channel_removeowner(token, channel_id, u_id2)
    clear()
# Token is invalid.
def test_invalid_token_remove():
    """test invalid token"""
    result = auth_register('hello@gmail.com', '123456', 'Bob', 'Hi')
    token = result['token']
    u_id = result['u_id']
    channel_id = channels_create(token, 'Mango', True)
    with pytest.raises(AccessError):
        channel_removeowner('hihihihi', channel_id, u_id)
    clear()
