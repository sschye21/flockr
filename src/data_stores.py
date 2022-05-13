'this is the data stores file for channels, auth, and messages data'
channels_data = []
messages_data = []
auth_data = []
reset_data = []
#pylint: disable = C0103, W0603
def channel_datastore():
    'data store for channels'
    global channels_data
    return channels_data

def auth_datastore():
    'data store for auth'
    global auth_data
    return auth_data

def messages_datastore():
    'data store for messages'
    global messages_data
    return messages_data

def resetcode_datastore():
    'datastore for resetcode'
    global reset_data
    return reset_data

def reset_resetcode_datastore():
    'rest for resetcode'
    global reset_data
    reset_data = []
    return reset_data

def reset_channels_datastore():
    'data store for resetting channels'
    global channels_data
    channels_data = []
    return channels_data

def reset_auth_datastore():
    'data store for resetting auth'
    global auth_data
    auth_data = []
    return auth_data

def reset_messages_datastore():
    'data store for resetting messages'
    global messages_data
    messages_data = []
    return messages_data
