'this includes all the test files for channels functions'
import pytest
from channels import channels_create, channels_list, channels_listall
from auth import auth_register
from error import InputError
from other import clear


#############################################################
#                   CHANNELS_CREATE                         #
#############################################################

def test_channels_create_public():
    'test function for channels create'


    result = auth_register("guest123@gmail.com", '123Asdf', "John", "Smith")
    token = result['token']

    channels_create(token, 'Thurs09Mango', True)
    clear()

def test_channels_create_private():
    'test function for channels create'

    result = auth_register("guest1234@gmail.com", '123Asdf', "John", "Smith")
    token = result['token']

    channels_create(token, 'Thurs09Mango', False)
    clear()

def test_name_too_long():
    'test function to raise error'

    result = auth_register("guest1235@gmail.com", '123Asdf', "John", "Smith")
    token = result['token']

    with pytest.raises(InputError):
        channels_create(token, 'a'*22, True)
    clear()

#############################################################
#                   CHANNELS_LIST                           #
#############################################################

def test_channel_list():
    'test function for channels list'

    result = auth_register("guest1236@gmail.com", '123Asdf', "John", "Smith")

    token = result['token']


    channel_id = channels_create(token, 'Thurs09Mango', False)

    assert (channels_list(token)[0]['channel_id'] == channel_id) # pylint: disable=C0325
    clear()
#############################################################
#                   CHANNELS_LISTALL                        #
#############################################################



def test_channel_listall():
    'test function for channels list'

    result = auth_register("guest1237@gmail.com", '123Asdf', "John", "Smith")
    token = result['token']


    result2 = auth_register("sid@gmail.com", '123Asdf', "jsds", "sdijwi")
    token2 = result2['token']


    channel1 = channels_create(token, 'Thurs09Mango', False)

    channel2 = channels_create(token2, 'disc', False)

    all_channels = channels_listall(token)
    id_collect = []
    for channels in all_channels:
        id_collect.append(channels['channel_id'])


    assert channel1 == id_collect[0]
    assert channel2 == id_collect[1]
    clear()
