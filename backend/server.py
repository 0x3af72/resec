import json
import base64
from typing import Dict, List, Tuple, Union
from string import ascii_letters, digits

import flask
from flask import Flask, request

import keys
import users
import index as index_page
from errors import *
from forms import *

app = Flask(__name__)

USERNAME_CHARS = ascii_letters + digits + "_"
GROUPNAME_CHARS = ascii_letters + digits + " _!()[]#@"

def JSON_CHECK():
    return request.headers["Content-Type"] == "application/json; charset=UTF-8"

@app.route("/", methods=["GET"])
def index():
    return index_page.INDEX_PAGE_DATA

@app.route("/register/", methods=["POST"])
def register():

    if not JSON_CHECK(): return INVALID_REQUEST_TYPE
    contents = request.get_json()
    if not verify_form(contents, REGISTER_FORM):
        return MALFORMED_DICT
    username = contents["username"]

    # check if username is taken
    if username in users.users:
        return UNAVAILABLE_USERNAME

    # check if username has illegal characters
    for c in username:
        if not c in USERNAME_CHARS:
            return INVALID_USERNAME

    # register user, and return private key
    priv, pub = keys.get_keyobjects() # real keys
    priv_ser, pub_ser = keys.get_priv(priv), keys.get_pub(pub)
    users.users[username] = users.USER(pub_ser)
    return {
        "code": 200,
        "data": priv_ser.decode(), # returned in string form
    }

@app.route("/verification_code/", methods=["POST"])
def verification_code():
    
    if not JSON_CHECK(): return INVALID_REQUEST_TYPE
    contents = request.get_json()
    if not verify_form(contents, VERIFICATION_CODE_FORM):
        return MALFORMED_DICT
    username = contents["username"]

    # check if username does not exist
    if not username in users.users:
        return NONEXISTENT_USERNAME

    # return code (in base64, decode client side)
    return {
        "code": 200,
        "data": base64.b64encode(users.users[username].code_enc).decode(),
    }

@app.route("/retrieve_messages/", methods=["POST"])
def retrieve_messages():

    if not JSON_CHECK(): return INVALID_REQUEST_TYPE
    contents = request.get_json()
    if not verify_form(contents, RETRIEVE_MESSAGES_FORM):
        return MALFORMED_DICT
    username = contents["username"]

    # check if username does not exist
    if not username in users.users:
        return NONEXISTENT_USERNAME

    # verify user's identity
    if not users.users[username].verify(contents["verification"]):
        return INCORRECT_VERIFICATION_CODE

    # return messages
    returned: List[
        Tuple[Dict[str, Union[str, bool]], str]
    ] = []
    for sender, mcontent in users.users[username].messages:
        returned.append((
            {"sender": sender.sender, "group": sender.group, "groupname": sender.groupname},
            base64.b64encode(mcontent).decode(),
        ))
    return {
        "code": 200,
        "data": json.dumps(returned),
    }

@app.route("/send_message/", methods=["POST"])
def send_message():
    
    if not JSON_CHECK(): return INVALID_REQUEST_TYPE
    contents = request.get_json()
    if not verify_form(contents, SEND_MESSAGE_FORM):
        return MALFORMED_DICT
    username = contents["username"]
    recipient = contents["recipient"] # can either be groupname or username of recipient

    # check if username or recipient do not exist
    if not username in users.users:
        return NONEXISTENT_USERNAME
    if not recipient in users.users and not contents["group"]:
        return NONEXISTENT_RECIPIENT

    # verify user's identy
    if not users.users[username].verify(contents["verification"]):
        return INCORRECT_VERIFICATION_CODE

    # if in group, check if group exists and user is in that group, and send to every user in group
    if contents["group"]:
        if not (recipient in users.groups and username in users.groups[recipient]):
            return INVALID_GROUP

        # yes this is meant to send to the sender too
        for u_recipient in users.groups[recipient]:

            # get public key
            u_pub = keys.get_pubobject(users.users[u_recipient].pub_ser)

            # send message
            users.users[u_recipient].messages.append((
                users.SENDER(username, True, recipient),
                keys.get_encrypted(contents["message"], u_pub),
            ))
    else: # just send normally without groups
    
        # get public keys of recipient and sender
        s_pub = keys.get_pubobject(users.users[username].pub_ser)
        r_pub = keys.get_pubobject(users.users[recipient].pub_ser)
        
        # send to sender and recipient
        users.users[username].messages.append((
            users.SENDER(username, False),
            keys.get_encrypted(contents["message"], s_pub),
        ))
        users.users[recipient].messages.append((
            users.SENDER(username, False),
            keys.get_encrypted(contents["message"], r_pub),
        ))

    return {
        "code": 200,
        "data": True,
    }

@app.route("/join_group/", methods=["POST"])
def join_group():
    
    if not JSON_CHECK(): return INVALID_REQUEST_TYPE
    contents = request.get_json()
    if not verify_form(contents, JOIN_GROUP_FORM):
        return MALFORMED_DICT
    username = contents["username"]
    groupname = contents["groupname"]

    # check if username does not exist
    if not username in users.users:
        return NONEXISTENT_USERNAME
    
    # verify user's identy
    if not users.users[username].verify(contents["verification"]):
        return INCORRECT_VERIFICATION_CODE

    # check if groupname is valid
    for c in groupname:
        if not c in GROUPNAME_CHARS:
            return INVALID_GROUP

    # check if already in group
    if groupname in users.users[username].groups:
        return ALREADY_IN_GROUP

    # create group if not exists and add user
    if not groupname in users.groups:
        users.groups[groupname] = set()
    users.groups[groupname].add(username)
    users.users[username].groups.add(groupname)
    return {
        "code": 200,
        "data": True,
    }

@app.route("/logout/", methods=["POST"])
def logout():

    if not JSON_CHECK(): return INVALID_REQUEST_TYPE
    contents = request.get_json()
    if not verify_form(contents, LOGOUT_FORM):
        return MALFORMED_DICT
    username = contents["username"]

    # check if username does not exist
    if not username in users.users:
        return NONEXISTENT_USERNAME
    
    # verify user's identy
    if not users.users[username].verify(contents["verification"]):
        return INCORRECT_VERIFICATION_CODE

    # delete from user dict and all groups
    for group in users.users[username].groups:
        users.groups[group].remove(username)
    del users.users[username]

    return {
        "code": 200,
        "data": True,
    }

@app.route("/leave_group/", methods=["POST"])
def leave_group():

    if not JSON_CHECK(): return INVALID_REQUEST_TYPE
    contents = request.get_json()
    if not verify_form(contents, LEAVE_GROUP_FORM):
        return MALFORMED_DICT
    username = contents["username"]
    groupname = contents["groupname"]

    # check if username does not exist
    if not username in users.users:
        return NONEXISTENT_USERNAME
    
    # verify user's identy
    if not users.users[username].verify(contents["verification"]):
        return INCORRECT_VERIFICATION_CODE

    # check if user isnt in group
    if (not groupname in users.users[username].groups) or (groupname not in users.groups):
        return INVALID_GROUP

    # leave group
    users.groups[groupname].remove(username)
    users.users[username].groups.remove(groupname)

    return {
        "code": 200,
        "data": True,
    }

app.run() # when deploying on pythonanywhere, remove this, and force https