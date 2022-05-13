'this includes all the test files for other functions'
import pytest #pylint: disable=W0611
from other import users_all, clear, search
from auth import auth_register
from channels import channels_create
from message import message_send
#############################################################
#                   USERS_ALL                               #
#############################################################
def test_users_all1():
    'test function for users all'

    clear()
    result = auth_register("guest1235@gmail.com", '123Asdf', "John", "Smith")
    token = result['token']
    u_id = result['u_id']

    all_users = users_all(token)


    assert all_users == [{

        'u_id': u_id,
        'email': "guest1235@gmail.com",
        'name_first': 'John',
        'name_last': 'Smith',
        'handle_str': 'johnsmith',

    }]


def test_users_all2():
    'test function for users all'

    clear()
    result = auth_register("guest1237@gmail.com", '123Asdf', "John", "Smith")
    token = result['token']
    u_id = result['u_id']

    result2 = auth_register("guest1@gmail.com", '123Asdf', "Sid", "Sat")

    all_users = users_all(token)


    assert all_users == [

        {
            'u_id': u_id,
            'email': "guest1237@gmail.com",
            'name_first': 'John',
            'name_last': 'Smith',
            'handle_str': 'johnsmith',
        },
        {
            'u_id': result2['u_id'],
            'email': "guest1@gmail.com",
            'name_first': 'Sid',
            'name_last': 'Sat',
            'handle_str': 'sidsat',
        }

    ]



#############################################################
#                   SEARCH                                  #
#############################################################
def test_search():
    'test case for search'
    clear()
    result = auth_register("guest1236@gmail.com", '123Asdf', "John", "Smith")
    token = result['token']

    channel_id = channels_create(token, 'Thurs09Mango', False)

    message_send(token, channel_id, 'Hello world')

    query = 'Hello world'

    find = search(token, query)

    for i in find:
        assert i['message'] == 'Hello world'

    clear()

def test_incorrectsearch():
    'test case for incorrect search'
    clear()
    result = auth_register("guest1238@gmail.com", '123Asdf', "John", "Smith")
    token = result['token']


    channel_id = channels_create(token, 'Thurs09Mango', False)

    message_send(token, channel_id, 'hello world')

    query = 'incorrect'

    find = search(token, query)

    counter = 0
    for i in find:
        if i['message'] != 'incorrect':
            counter = counter + 1

    assert counter == 0

    clear()

def test_multiplesearch():
    'test messages in different channels'
    clear()

    result = auth_register("guest1241@gmail.com", '123Asdf', "John", "Smith")
    token = result['token']

    channel_id = channels_create(token, 'Thurs09Mango', False)
    message_send(token, channel_id, 'Hello world')


    channel_id2 = channels_create(token, 'Discord', False)
    message_send(token, channel_id2, 'Hello world')

    query = 'Hello world'

    find = search(token, query)

    counter = 0
    for i in find:
        if i['message'] == 'Hello world':
            counter = counter + 1

    assert counter == 2


    clear()


def test_blank():
    'test empty message'
    clear()

    result = auth_register("guest1239@gmail.com", '123Asdf', "John", "Smith")
    token = result['token']

    channel_id = channels_create(token, 'Thurs09Mango', False)

    message_send(token, channel_id, "")

    query = ""

    find = search(token, query)

    counter = 0
    for i in find:
        if i['message'] == "":
            counter = counter + 1

    assert counter == 1
    clear()
