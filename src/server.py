'''server doc'''
from json import dumps
from flask import Flask, request
from flask_cors import CORS
#pylint: disable = C0301
from auth import auth_register, auth_login, auth_logout, auth_passwordreset_request, auth_passwordreset_reset
from data_stores import auth_datastore, channel_datastore, resetcode_datastore
from channel import channel_invite, channel_details, channel_join, channel_leave, channel_messages, channel_addowner, channel_removeowner
from channels import channels_create, channels_list, channels_listall
from message import message_send, message_remove, message_edit, message_react, message_unreact, message_pin, message_unpin, message_sendlater
from user import user_profile, user_profile_sethandle, user_profile_setname, user_profile_setemail, user_profile_uploadphoto
from error import InputError
from other import clear, search, users_all, admin_userpermission_change
from standup import standup_active, standup_send, standup_start
#pylint:disable = C0103
def defaultHandler(err):
    """error message"""
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    """echo sample"""
    data = request.args.get('data')
    if data == 'echo':
        raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })

@APP.route("/auth/user_info", methods=['GET'])
def user_info():
    """access all users info"""
    auth_data = auth_datastore()
    return dumps(auth_data)

@APP.route("/auth/resetcode", methods=['GET'])
def resetcode_info():
    """access reset info"""
    reset_data = resetcode_datastore()
    return dumps(reset_data)

@APP.route("/channel/channel_info", methods=['GET'])
def channel_info():
    """access all channesl info"""
    channels_data = channel_datastore()
    return dumps(channels_data)

##############
# AUTH_LOGIN #
##############
@APP.route("/auth/login", methods=['POST'])
def auth_login_http():
    """user login"""
    payload = request.get_json()
    result = auth_login(payload['email'], payload['password'])
    return dumps({
        'u_id': result['u_id'],
        'token': result['token']
    })
@APP.route("/auth/logout", methods=['POST'])
def auth_logout_http():
    """user logout"""
    payload = request.get_json()
    result = auth_logout(payload['token'])
    return dumps({
        'is_success': result['is_success']
    })

@APP.route("/auth/register", methods=['POST'])
def auth_register_http():
    """register a user"""
    payload = request.get_json()
    result = auth_register(payload['email'], payload['password'], payload['name_first'], payload['name_last'])
    return dumps({
        'u_id': result['u_id'],
        'token': result['token']
    })

@APP.route("/channel/invite", methods=['POST'])
def channel_invite_http():
    """invite a user to a channel"""
    payload = request.get_json()
    channel_invite(payload['token'], payload['channel_id'], payload['u_id'])
    return {}

@APP.route("/channel/details", methods=['GET'])
def channel_details_http():
    """view a channel details"""
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    details = channel_details(token, channel_id)
    return dumps({
        'name': details['name'],
        'owner_members': details['owner_members'],
        'all_members': details['all_members']
    })

@APP.route("/channels/create", methods=['POST'])
def channels_create_http():
    """Functions to create a new channel"""
    payload = request.get_json()
    channel_id = channels_create(payload['token'], payload['name'], payload['is_public'])
    return dumps({
        'channel_id': channel_id
    })

@APP.route("/message/send", methods=['POST'])
def message_send_http():
    """send a message to a channel"""
    payload = request.get_json()
    message_id = message_send(payload['token'], payload['channel_id'], payload['message'])
    return dumps({
        'message_id':message_id
    })

@APP.route("/message/remove", methods=['DELETE'])
def message_remove_http():
    """delete a message in a channel"""
    payload = request.get_json()
    message_remove(payload['token'], payload['message_id'])
    return {}

@APP.route("/message/edit", methods=['PUT'])
def message_edit_http():
    """edit message"""
    payload = request.get_json()
    message_edit(payload['token'], int(payload['message_id']), payload['message'])
    return {}

@APP.route("/admin/change", methods=['POST'])
def admin_change_http():
    """change permissions of member to admin"""
    payload = request.get_json()
    admin_userpermission_change(payload['token'], payload['u_id'], payload['permission_id'])
    return {}

@APP.route("/message/sendlater", methods=['POST'])
def sendlater_http():
    'send message later'
    payload = request.get_json()
    token = payload['token']
    channel_id = int(payload['channel_id'])
    message = payload['message']
    time_sent = payload['time_sent']
    result = message_sendlater(token, channel_id, message, time_sent)
    return dumps({
        'message_id':result
    })


######################### channel functions #########################
@APP.route("/channel/join", methods=['POST'])
def channel_join_http():
    """join a channel"""
    payload = request.get_json()
    channel_join(payload['token'], payload['channel_id'])
    return {}

@APP.route("/channel/leave", methods=['POST'])
def channel_leave_http():
    """leave a channel"""
    payload = request.get_json()
    channel_leave(payload['token'], payload['channel_id'])
    return {}

####################
# CHANNEL_MESSAGES #
####################

@APP.route("/channel/messages", methods=['GET'])
def channel_messages_http():
    """returns message information"""
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    start = int(request.args.get('start'))
    result = channel_messages(token, channel_id, start)

    return dumps({
        'messages': result['messages'],
        'start': result['start'],
        'end': result['end']
    })

@APP.route("/channel/addowner", methods=['POST'])
def channel_addowner_http():
    """add owner into channel"""
    payload = request.get_json()
    channel_addowner(payload['token'], payload['channel_id'], payload['u_id'])
    return {}

@APP.route("/channel/removeowner", methods=['POST'])
def channel_removeowner_http():
    """remove owner from channel"""
    payload = request.get_json()
    channel_removeowner(payload['token'], payload['channel_id'], payload['u_id'])
    return dumps(payload)

@APP.route("/user/user_profile", methods=['GET'])
def user_profile_http():
    """returns user information"""
    token = request.args.get('token')
    u_id = int(request.args.get('u_id'))
    prof = user_profile(token, u_id)
    return dumps({
        'user': prof['user']
    })

@APP.route("/user/profile/sethandle", methods=['PUT'])
def user_profile_sethandle_http():
    """change handle_str"""
    payload = request.get_json()
    user_profile_sethandle(payload['token'], payload['handle_str'])
    return {}

@APP.route("/user/profile/setname", methods=['PUT'])
def user_profile_setname_http():
    """change name"""
    payload = request.get_json()
    user_profile_setname(payload['token'], payload['name_first'], payload['name_last'])
    return {}

@APP.route("/user/profile/setemail", methods=['PUT'])
def user_profile_setemail_http():
    """change email"""
    payload = request.get_json()
    user_profile_setemail(payload['token'], payload['email'])
    return {}

#############################################################
#                   CHANNELS_LIST                         #
#############################################################
@APP.route("/channels/list", methods=['GET'])
def channels_list_http():
    """server route for channels list"""
    token = request.args.get('token')
    chann_inf = channels_list(token)
    return dumps({
        'channels': chann_inf
    })

#############################################################
#                   CHANNELS_LISTALL                         #
#############################################################
@APP.route("/channels/listall", methods=['GET'])
def channels_listall_http():
    'server route for channels listall'

    token = request.args.get('token')
    chann_inf = channels_listall(token)

    return  dumps({
        'channels':chann_inf
    })



#############################################################
#                   SEARCH                                  #
#############################################################
@APP.route("/search", methods=['GET'])
def search_http():
    'server route for search'

    token = request.args.get('token')
    query = request.args.get('query_str')

    check = search(token, query)
    result = []
    ##check is a list contains dicts
    for i in check:
        result.append(i['message'])
    return dumps({
        'messages': result
    })



#############################################################
#                   USERS_ALL                               #
#############################################################
@APP.route("/users/all", methods=['GET'])
def usersall_http():
    'server route for usersall'

    token = request.args.get('token')
    payload = {
        'token': token
    }
    info = users_all(payload)
    return dumps({
        'users': info
    })

#############################################################
#                   CLEAR                                   #
#############################################################
@APP.route("/clear", methods=['DELETE'])
def clear_http():
    'server route for clear'

    clear()
    return dumps({})

@APP.route("/admin/userpermission/change", methods=['POST'])
def permission_change():
    'change permission id for user'
    payload = request.get_json()
    admin_userpermission_change(payload['token'], payload['u_id'], payload['permission_id'])
    return {}

@APP.route("/standup/start", methods=['POST'])
def standup_start_http():
    'start a standup queue'
    payload = request.get_json()
    token = payload['token']
    channel_id = int(payload['channel_id'])
    length = int(payload['length'])
    result = standup_start(token, channel_id, length)
    return dumps(result)

@APP.route("/standup/active", methods=['GET'])
def standup_active_http():
    'check if standup is active'
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    result = standup_active(token, channel_id)
    return dumps(result)

@APP.route("/standup/send", methods=['POST'])
def standup_send_http():
    'send message to standup queue'
    payload = request.get_json()
    standup_send(payload['token'], payload['channel_id'], payload['message'])

    return {}


#############################################################
#                   PASSWORD_REQUEST                        #
#############################################################
@APP.route("/auth/passwordreset/request", methods=['POST'])
def request_http():
    'server route for password request'

    payload = request.get_json()
    auth_passwordreset_request(payload['email'])

    return dumps({})

#############################################################
#                   PASSWORD_RESET                        #
#############################################################
@APP.route("/auth/passwordreset/reset", methods=['POST'])
def reset_http():
    'server route for password reset'

    payload = request.get_json()
    auth_passwordreset_reset(payload['reset_code'], payload['new_password'])

    return {}

############################
# USER_PROFILE_UPLOADPHOTO #
############################
@APP.route("/user/profile/uploadphoto", methods=['POST'])
def user_profile_uploadphoto_http():
    '''user_profile_uploadphoto server route'''
    payload = request.get_json()
    user_profile_uploadphoto(payload['token'], payload['img_url'], payload['x_start'], payload['y_start'], payload['x_end'], payload['y_end'])
    return {}

#################
# MESSAGE_REACT #
#################
@APP.route("/message/react", methods=['POST'])
def message_react_http():
    '''message_react server route'''
    payload = request.get_json()
    message_react(payload['token'], payload['message_id'], payload['react_id'])
    return {}

###################
# MESSAGE_UNREACT #
###################
@APP.route("/message/unreact", methods=['POST'])
def message_unreact_http():
    '''message_unreact server route'''
    payload = request.get_json()
    message_unreact(payload['token'], payload['message_id'], payload['react_id'])
    return {}

#################
# MESSAGE_PIN #
#################
@APP.route("/message/pin", methods=['POST'])
def message_pin_http():
    '''message_react server route'''
    payload = request.get_json()
    message_pin(payload['token'], payload['message_id'])
    return {}

###################
# MESSAGE_UNPIN #
###################
@APP.route("/message/unpin", methods=['POST'])
def message_unpin_http():
    '''message_unreact server route'''
    payload = request.get_json()
    message_unpin(payload['token'], payload['message_id'])
    return {}

if __name__ == "__main__":
    APP.run(port=0) # Do not edit this port
