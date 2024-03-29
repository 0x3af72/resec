####################################################################################
#
# Written by cry6.
# Some testcases. Client's api.py is just a modified version of this.
#
####################################################################################

from requests import post
from keys import *
import json
import base64

# setup
base_url = "http://192.168.1.7:5000"
# base_url = "https://czy6.pythonanywhere.com"
headers = {"Content-Type": "application/json; charset=UTF-8"}

# test urls
REGISTER_URL = "/register"
RETRIEVE_MESSAGES_URL = "/retrieve_messages"
VERIFICATION_CODE_URL = "/verification_code"
SEND_MESSAGE_URL = "/send_message"
JOIN_GROUP_URL = "/join_group"
LOGOUT_URL = "/logout"
LEAVE_GROUP_URL = "/leave_group"
BLOCK_USER_URL = "/block_user"
UNBLOCK_USER_URL = "/unblock_user"
RETRIEVE_CONTACTS_URL = "/retrieve_contacts"
GROUP_MEMBERS_URL = "/group_members"

# RIght now just putting everything into functions so easier to test

def register(username):
    REGISTER_DATA = {
        "username": username,
    }
    r = post(base_url + REGISTER_URL, json=REGISTER_DATA, headers=headers)
    priv_ser = r.json()["data"]
    priv = get_privobject(priv_ser.encode())
    return priv

def get_vcode(username, priv):
    REGISTER_DATA = {
        "username": username,
    }
    r = post(base_url + VERIFICATION_CODE_URL, json=REGISTER_DATA, headers=headers)
    code_encrypted = base64.b64decode(r.json()["data"])
    code_raw = get_decrypted(code_encrypted, priv)
    return code_raw

def retrieve_messages(username, channel, group, priv):
    RETRIEVE_MESSAGES_DATA = {
        "username": username, "group": group, "channel": channel
    }
    RETRIEVE_MESSAGES_DATA["verification"] = get_vcode(username, priv)
    r = post(base_url + RETRIEVE_MESSAGES_URL, json=RETRIEVE_MESSAGES_DATA, headers=headers)
    messages = [
        (sender, get_decrypted(base64.b64decode(message), priv))
        for sender, message in json.loads(r.json()["data"])
    ]
    return messages

def send_message(username, recipient, group, message, priv):
    SEND_MESSAGE_DATA = {
        "username": username, "verification": get_vcode(username, priv), "recipient": recipient,
        "group": group, "message": message,
    }
    r = post(base_url + SEND_MESSAGE_URL, json=SEND_MESSAGE_DATA, headers=headers)
    print("message send" + (" success" if r.json()["data"] else " fail"))

def join_group(username, groupname, priv):
    JOIN_GROUP_DATA = {
        "username": username, "groupname": groupname, "verification": get_vcode(username, priv)
    }
    r = post(base_url + JOIN_GROUP_URL, json=JOIN_GROUP_DATA, headers=headers)
    print("join group" + (" success" if r.json()["data"] else " fail"))

def logout(username, priv):
    LOGOUT_DATA = {
        "username": username, "verification": get_vcode(username, priv)
    }
    r = post(base_url + LOGOUT_URL, json=LOGOUT_DATA, headers=headers)
    print("logout success" + (" success" if r.json()["data"] else " fail"))

def leave_group(username, groupname, priv):
    LEAVE_GROUP_DATA = {
        "username": username, "groupname": groupname, "verification": get_vcode(username, priv)
    }
    r = post(base_url + LEAVE_GROUP_URL, json=LEAVE_GROUP_DATA, headers=headers)
    print("keave group" + (" success" if r.json()["data"] else " fail"))

def block_user(username, blocked, priv):
    BLOCK_USER_DATA = {
        "username": username, "blocked": blocked, "verification": get_vcode(username, priv)
    }
    r = post(base_url + BLOCK_USER_URL, json=BLOCK_USER_DATA, headers=headers)
    print("blocked" if r.json()["data"] else "fail")

def unblock_user(username, blocked, priv):
    UNBLOCK_USER_DATA = {
        "username": username, "blocked": blocked, "verification": get_vcode(username, priv)
    }
    r = post(base_url + UNBLOCK_USER_URL, json=UNBLOCK_USER_DATA, headers=headers)
    print("unblocked" if r.json()["data"] else "fail")

def retrieve_contacts(username, priv):
    RETRIEVE_CONTACTS_DATA = {
        "username": username, "verification": get_vcode(username, priv)
    }
    r = post(base_url + RETRIEVE_CONTACTS_URL, json=RETRIEVE_CONTACTS_DATA, headers=headers)
    print(r.json()["data"])

def group_members(username, groupname, priv):
    GROUP_MEMBERS_DATA = {
        "username": username, "groupname": groupname, "verification": get_vcode(username, priv)
    }
    r = post(base_url + GROUP_MEMBERS_URL, json=GROUP_MEMBERS_DATA, headers=headers)
    print(r.json())
    print(r.json()["data"])

john = register("john")
doe = register("doe")
tom = register("tom")

join_group("john", "hello", john)
join_group("doe", "hello", doe)
join_group("tom", "hello", tom)
# logout("tom", tom)
# leave_group("tom", "hello", tom)

# send_message("john", "hello", True, "testn", john)
# john_messages = retrieve_messages("john", john)
# print(john_messages)
# doe_messages = retrieve_messages("doe", "hello", True, doe)
# print(doe_messages)
# tom_messages = retrieve_messages("tom", "hello", True, tom)
# print(tom_messages)

# block_user("john", "doe", john)
# unblock_user("john", "doe", john)
# send_message("doe", "john", False, "hello", doe)

send_message("john", "hello", True, "group send test", john)
print(retrieve_messages("john", "hello", True, john))
print(retrieve_messages("doe", "hello", True, doe))
print(retrieve_messages("tom", "hello", True, tom))

send_message("john", "doe", False, "dm test", john)
print(retrieve_messages("john", "doe", False, john))
print(retrieve_messages("doe", "john", False, doe))

retrieve_contacts("john", john)
retrieve_contacts("doe", doe)
retrieve_contacts("tom", tom)

# leave_group("john", "hello", john)
group_members("john", "hello", john)