Assumptions File for Thu09MangoTeam4:
#Brittany Li
#Michael Comino
#Siddarth Satyavolu
#Steven Chye
#Zheng Hengzhan

auth_register: 
    - When new user registers an account, he/she does not have a middle name 
    - User_id is generated from 0 to 1000 without repeating, we assume no more than 1000 users in the test 
    - Token should be a randomly generated key, we set token to be equal to str(u_id) in Iteration 1
    - When user is registered, they are automatically logged in and a valid token is generated

channel_invite:
    - Only owners of the channel can invite others into the channel 

channel_details:
    - Both owners and members have access to check the details of their channels 					

channel_addower:
    - channel_addowner only promotes a member 

channel_removeowner:
    - When owner is removed using channel_removeowner function, they become a member 

channels_create:
    - Assumes the user who created the channel to also be the owner of the channel
    
user_profile_setemail:
    - A user can change his email to his own email and it will just update

user_profile_setname:
    - First name and last name can be between 1 and 50 characters inclusive

user_profile_sethandle:
    - A user cannot change his handle to his current one, raises an error

message_edit:
    - Owner of a channel can edit any message 
    - Member of a channel can only edit their own message 
    
admin_userpermissions_change 
    - A permission_id of 1  global owner with owner – like privileges in every channel 
    - A permission_id of 2  member without any special privileges 
    - The first user who registered on slackr is automatically a global owner 
    - All users after are automatically members with a permission_id of 2 
    - Every time a new channel is created, global owners are added to the list of owners in the channel
    - A user cannot change his own permissions

auth_password_request:
    - User can request as many times as they like

message_react:
    - User cannot react to a message twice

message_sendlater:
    - User can edit his own message without it being sent yet but it has been set to be send
    - Message cannot be removed after it has been set to be sent, can only be removed after it has been officially sent into the channel

standup_start:
    - anyone can call function

standup_end:
    - anyone can call function
