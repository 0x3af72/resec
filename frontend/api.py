####################################################################################
#
# Written by cry6.
# Quick remark: The code here is horrendous.
#
####################################################################################

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
    
    # initialize api response given whether successful, error message and returned data
    def __init__(self, success: bool, error_message: str, data: Any) -> None:
        self.success = success
        self.error_message = error_message
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

# verification code function
def get_vcode(username: str, priv: rsa.RSAPrivateKey) -> API_RESPONSE:
    resp = POST(VERIFICATION_CODE_URL, {
        "username": username,
    })

    if resp["code"] != 200:
        return API_RESPONSE(False, resp["error"], None)
    e_code = base64.b64decode(resp["data"])
    return API_RESPONSE(True, "", get_decrypted(e_code, priv))

# api functions to be called from main script
def register(username: str) -> API_RESPONSE:
    resp = POST(REGISTER_URL, {"username": username,})

    if resp["code"] != 200:
        return API_RESPONSE(False, resp["error"], None)
    priv_ser = resp["data"]
    return API_RESPONSE(True, "", get_privobject(priv_ser.encode()))

def retrieve_messages(username: str, priv: rsa.RSAPrivateKey, channel: str, group: bool) -> API_RESPONSE:
    POST_DICT = {
        "username": username,
        "group": group,
        "channel": channel,
    }

    # get verification code: assign to the dict, return stuff if doesnt work.
    vcode = get_vcode(username, priv)
    if not vcode:
        return vcode
    POST_DICT["verification"] = vcode.data
    
    resp = POST(RETRIEVE_MESSAGES_URL, POST_DICT)

    if resp["code"] != 200:
        return API_RESPONSE(False, resp["error"], None)
    messages = [
        (sender, get_decrypted(base64.b64decode(message), priv))
        for sender, message in json.loads(resp["data"])
    ]
    return API_RESPONSE(True, "", messages)

def send_message(username: str, priv: rsa.RSAPrivateKey, recipient: str, group: bool, message: str) -> API_RESPONSE:
    POST_DICT = {
        "username": username, "recipient": recipient,
        "group": group, "message": message,
    }

    # get verification code: assign to the dict, return stuff if doesnt work.
    vcode = get_vcode(username, priv)
    if not vcode:
        return vcode
    POST_DICT["verification"] = vcode.data

    resp = POST(SEND_MESSAGE_URL, POST_DICT)

    if resp["code"] != 200:
        return API_RESPONSE(False, resp["error"], None)
    return API_RESPONSE(True, "", None)
    
def join_group(username: str, priv: rsa.RSAPrivateKey, groupname: str) -> API_RESPONSE:
    POST_DICT = {"username": username, "groupname": groupname}

    # get verification code: assign to the dict, return stuff if doesnt work.
    vcode = get_vcode(username, priv)
    if not vcode:
        return vcode
    POST_DICT["verification"] = vcode.data

    resp = POST(JOIN_GROUP_URL, POST_DICT)
    if resp["code"] != 200:
        return API_RESPONSE(False, resp["error"], None)
    return API_RESPONSE(True, "", None)

def logout(username: str, priv: rsa.RSAPrivateKey) -> API_RESPONSE:
    POST_DICT = {"username": username}

    # get verification code: assign to the dict, return stuff if doesnt work.
    vcode = get_vcode(username, priv)
    if not vcode:
        return vcode
    POST_DICT["verification"] = vcode.data

    resp = POST(LOGOUT_URL, POST_DICT)
    if resp["code"] != 200:
        return API_RESPONSE(False, resp["error"], None)
    return API_RESPONSE(True, "", None)

def leave_group(username: str, priv: rsa.RSAPrivateKey, groupname: str) -> API_RESPONSE:
    POST_DICT = {"username": username, "groupname": groupname}

    # get verification code: assign to the dict, return stuff if doesnt work.
    vcode = get_vcode(username, priv)
    if not vcode:
        return vcode
    POST_DICT["verification"] = vcode.data

    resp = POST(LEAVE_GROUP_URL, POST_DICT)
    if resp["code"] != 200:
        return API_RESPONSE(False, resp["error"], None)
    return API_RESPONSE(True, "", None)

# WORK ON THIS RN
def block_user(username: str, priv: rsa.RSAPrivateKey, blocked: str) -> API_RESPONSE:
    POST_DICT = {"username": username, "blocked": blocked}

    # get verification code: assign to the dict, return stuff if doesnt work.
    vcode = get_vcode(username, priv)
    if not vcode:
        return vcode
    POST_DICT["verification"] = vcode.data

    resp = POST(BLOCK_USER_URL, POST_DICT)
    if resp["code"] != 200:
        return API_RESPONSE(False, resp["error"], None)
    return API_RESPONSE(True, "", None)

def unblock_user(username: str, priv: rsa.RSAPrivateKey, blocked: str) -> API_RESPONSE:
    POST_DICT = {"username": username, "blocked": blocked}

    # get verification code: assign to the dict, return stuff if doesnt work.
    vcode = get_vcode(username, priv)
    if not vcode:
        return vcode
    POST_DICT["verification"] = vcode.data

    resp = POST(UNBLOCK_USER_URL, POST_DICT)
    if resp["code"] != 200:
        return API_RESPONSE(False, resp["error"], None)
    return API_RESPONSE(True, "", None)

def retrieve_contacts(username: str, priv: rsa.RSAPrivateKey) -> API_RESPONSE:
    POST_DICT = {"username": username}

    # get verification code: assign to the dict, return stuff if doesnt work.
    vcode = get_vcode(username, priv)
    if not vcode:
        return vcode
    POST_DICT["verification"] = vcode.data

    resp = POST(RETRIEVE_CONTACTS_URL, POST_DICT)
    if resp["code"] != 200:
        return API_RESPONSE(False, resp["error"], None)
    return API_RESPONSE(True, "", resp["data"])

def group_members(username: str, priv: rsa.RSAPrivateKey, groupname: str) -> API_RESPONSE:
    POST_DICT = {"username": username, "groupname": groupname}

    # get verification code: assign to the dict, return stuff if doesnt work.
    vcode = get_vcode(username, priv)
    if not vcode:
        return vcode
    POST_DICT["verification"] = vcode.data

    resp = POST(GROUP_MEMBERS_URL, POST_DICT)
    if resp["code"] != 200:
        return API_RESPONSE(False, resp["error"], None)
    return API_RESPONSE(True, "", resp["data"])

if __name__ == "__main__":

    # testing

    john = register("john").data
    doe = register("doe").data
    tom = register("tom").data

    join_group("john", john, "hello")
    join_group("doe", doe, "hello")
    join_group("tom", tom, "hello")
    # logout("tom", tom)
    # leave_group("doe", doe, "hello")

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

    send_message("john", john, "hello", True, "group send test")
    print(retrieve_messages("doe", doe, "hello", True).data)

    send_message("john", john, "doe", False, "dm test")
    print(retrieve_messages("doe", doe, "john", False).data)

    print(retrieve_contacts("john", john).data)
    print(retrieve_contacts("doe", doe).data)
    print(retrieve_contacts("tom", tom).data)

    # leave_group("john", "hello", john)
    print(group_members("john", john, "hello").data)