import json
import base64
from typing import Any

from requests import post

from keys import *

# setup
base_url = "http://127.0.0.1:5000"
headers = {"Content-Type": "application/json; charset=UTF-8"}

# url routes
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

# object returned from api call
class API_RESPONSE:
    
    # initialize api response given whether successful, error code and returned data
    def __init__(self, success: bool, error_code: str, data: Any) -> None:
        self.success = success
        self.error_code = error_code
        self.data = data

    # quick check whether successful
    def __bool__(self) -> bool:
        return self.success

# shortcut to use requests.post
def POST(path: str, json: Any) -> Any:
    resp = post(
        base_url + path,
        json=json,
        headers=headers,
    )
    return resp.json()

# api functions to be called from main script

def register(username: str) -> API_RESPONSE:

    resp = POST(REGISTER_URL, {
        "username": username,
    })

    if resp["code"] == 200:
        priv_ser = resp["data"]
        return API_RESPONSE(True, "", get_privobject(priv_ser.encode()))
    return API_RESPONSE(False, resp["error"])

def get_vcode(username: str, priv: rsa.RSAPrivateKey) -> API_RESPONSE:

    resp = POST(VERIFICATION_CODE_URL, {
        "username": username,
    })

    if resp["code"] == 200:
        e_code = base64.b64decode(resp["data"])
        return API_RESPONSE(True, "", get_decrypted(e_code, priv))
    return API_RESPONSE(False, resp["error"])

# REPORT ERROR WHEN VCODE WRONG... HOW?
def retrieve_messages(username, channel, group, priv):
    
    resp = POST(RETRIEVE_MESSAGES_URL, {
        "username": username, "group": group, "channel": channel,
        "verification": get_vcode(username, priv).data
    })
    # r = post(base_url + RETRIEVE_MESSAGES_URL, json=RETRIEVE_MESSAGES_DATA, headers=headers)
    # messages = [
    #     (sender, get_decrypted(base64.b64decode(message), priv))
    #     for sender, message in json.loads(r.json()["data"])
    # ]
    # return messages

def send_message(username, recipient, group, message, priv):
    SEND_MESSAGE_DATA = {
        "username": username, "verification": get_vcode(username, priv).data, "recipient": recipient,
        "group": group, "message": message,
    }
    r = post(base_url + SEND_MESSAGE_URL, json=SEND_MESSAGE_DATA, headers=headers)
    print("message send" + (" success" if r.json()["data"] else " fail"))

def join_group(username, groupname, priv):
    JOIN_GROUP_DATA = {
        "username": username, "groupname": groupname, "verification": get_vcode(username, priv).data
    }
    r = post(base_url + JOIN_GROUP_URL, json=JOIN_GROUP_DATA, headers=headers)
    print("join group" + (" success" if r.json()["data"] else " fail"))

def logout(username, priv):
    LOGOUT_DATA = {
        "username": username, "verification": get_vcode(username, priv).data
    }
    r = post(base_url + LOGOUT_URL, json=LOGOUT_DATA, headers=headers)
    print("logout success" + (" success" if r.json()["data"] else " fail"))

def leave_group(username, groupname, priv):
    LEAVE_GROUP_DATA = {
        "username": username, "groupname": groupname, "verification": get_vcode(username, priv).data
    }
    r = post(base_url + LEAVE_GROUP_URL, json=LEAVE_GROUP_DATA, headers=headers)
    print("keave group" + (" success" if r.json()["data"] else " fail"))

def block_user(username, blocked, priv):
    BLOCK_USER_DATA = {
        "username": username, "blocked": blocked, "verification": get_vcode(username, priv).data
    }
    r = post(base_url + BLOCK_USER_URL, json=BLOCK_USER_DATA, headers=headers)
    print("blocked" if r.json()["data"] else "fail")

def unblock_user(username, blocked, priv):
    UNBLOCK_USER_DATA = {
        "username": username, "blocked": blocked, "verification": get_vcode(username, priv).data
    }
    r = post(base_url + UNBLOCK_USER_URL, json=UNBLOCK_USER_DATA, headers=headers)
    print("unblocked" if r.json()["data"] else "fail")

def retrieve_contacts(username, priv):
    RETRIEVE_CONTACTS_DATA = {
        "username": username, "verification": get_vcode(username, priv).data
    }
    r = post(base_url + RETRIEVE_CONTACTS_URL, json=RETRIEVE_CONTACTS_DATA, headers=headers)
    print(r.json()["data"])

def group_members(username, groupname, priv):
    GROUP_MEMBERS_DATA = {
        "username": username, "groupname": groupname, "verification": get_vcode(username, priv).data
    }
    r = post(base_url + GROUP_MEMBERS_URL, json=GROUP_MEMBERS_DATA, headers=headers)
    print(r.json())
    print(r.json()["data"])

john = register("john").data
doe = register("doe").data
tom = register("tom").data

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