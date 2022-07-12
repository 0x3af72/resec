import json
import time
import base64
from typing import Dict, List, Tuple, Union
from string import ascii_letters, digits

import flask
from flask import Flask, request

import keys
import users
import pages as pages
from errors import *
from forms import *

app = Flask(__name__)

USERNAME_CHARS = ascii_letters + digits + "_"
GROUPNAME_CHARS = ascii_letters + digits + " _!()[]#@"
GROUPNAME_MAX = 50
USERNAME_MAX = 20
MESSAGE_MAX = 3000
NO_VERIFICATION_PATHS = {"/register", "/verification_code"}

request_logs: Dict[str, List[float]] = {}
MAX_REQUESTS_PER_INTERVAL = 50

def JSON_CHECK():
    return request.headers["Content-Type"] == "application/json; charset=UTF-8"

# ====================== WEBPAGE URLS ======================

@app.route("/", methods=["GET"])
def index():
    return pages.INDEX_PAGE_DATA

@app.route("/w")
def index_w():
    return pages.W_PAGE_DATA

@app.route("/x1kvs5f50ft5yhq1")
def x1kvs5f50ft5yhq1():
    return pages.x1kvs5f50ft5yhq1

@app.route("/oghepki3k3vnrxy8/")
def oghepki3k3vnrxy8():
    return pages.oghepki3k3vnrxy8

# ====================== POST URLS ======================

@app.before_request
def before_request():

    # if pythonanywhere, use xrealip, else use remote_addr
    ip = request.headers["X-Real-IP"] if "X-Real-IP" in request.headers else request.remote_addr

    # add to log if not yet
    if not ip in request_logs:
        request_logs[ip] = []
    
    # remove requests that were more than 5 secs ago
    cur_time = time.time()
    request_logs[ip] = [hit for hit in request_logs[ip] if (cur_time - hit) < 5]
    
    # check if hits are max already
    if len(request_logs[ip]) >= MAX_REQUESTS_PER_INTERVAL:
        return TOO_MANY_HITS

    # add hit
    request_logs[ip].append(cur_time)

    if request.method == "POST":

        # check if json
        if not JSON_CHECK():
            return INVALID_REQUEST_TYPE
        
        # check if invalid verification code and user exists
        if not request.path in NO_VERIFICATION_PATHS:
            contents = request.get_json()

            # check if contains these fields
            if (not "username" in contents) or (not "verification" in contents):
                return MALFORMED_DICT

            # check if user exists
            if not contents["username"] in users.users:
                return NONEXISTENT_USERNAME
            
            # verify user identity
            if not users.users[contents["username"]].verify(contents["verification"]):
                return INCORRECT_VERIFICATION_CODE

@app.route("/register", methods=["POST"])
def register():

    contents = request.get_json()
    if not verify_form(contents, REGISTER_FORM):
        return MALFORMED_DICT
    username = contents["username"]

    # check if username is taken
    if username in users.users:
        return UNAVAILABLE_USERNAME

    # check if username has illegal characters or is too long
    if len(username) > USERNAME_MAX: return TOO_MANY_CHARACTERS
    for c in username:
        if not c in USERNAME_CHARS:
            return INVALID_USERNAME

    # register user, add blocked list, and return private key
    priv, pub = keys.get_keyobjects() # real keys
    priv_ser, pub_ser = keys.get_priv(priv), keys.get_pub(pub)
    users.users[username] = users.USER(pub_ser)
    users.blocks[username] = set()
    return {
        "code": 200,
        "data": priv_ser.decode(), # returned in string form
    }

@app.route("/verification_code", methods=["POST"])
def verification_code():
    
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

@app.route("/retrieve_messages", methods=["POST"])
def retrieve_messages():

    contents = request.get_json()
    if not verify_form(contents, RETRIEVE_MESSAGES_FORM):
        return MALFORMED_DICT
    username = contents["username"]
    channel = contents["channel"]

    # return messages in group
    if contents["group"]:
        # check if not in group
        if not channel in users.users[username].groups:
            return INVALID_GROUP

        returned: List[Tuple[str, str]] = [
            (sender, base64.b64encode(mcontent).decode())
            for sender, mcontent in users.users[username].groups[channel]
        ]

    # return messages in dm
    else:
        # check if not in contacts
        if not channel in users.users[username].contacts:
            return INVALID_CONTACT

        returned: List[Tuple[str, str]] = [
            (username if sender else channel, base64.b64encode(mcontent).decode())
            for sender, mcontent in users.users[username].contacts[channel]
        ]

    return {
        "code": 200,
        "data": json.dumps(returned),
    }

@app.route("/send_message", methods=["POST"])
def send_message():
    
    contents = request.get_json()
    if not verify_form(contents, SEND_MESSAGE_FORM):
        return MALFORMED_DICT
    username = contents["username"]
    recipient = contents["recipient"] # can either be groupname or username of recipient

    # check if recipient does not exist
    if not recipient in users.users and not contents["group"]:
        return NONEXISTENT_RECIPIENT

    # check if message too long
    if len(contents["message"]) > MESSAGE_MAX:
        return TOO_MANY_CHARACTERS

    # if in group, check if group exists and user is in that group, and send to every user in group
    if contents["group"]:
        if not (recipient in users.groups and username in users.groups[recipient]):
            return INVALID_GROUP

        # yes this is meant to send to the sender too
        for u_recipient in users.groups[recipient]:

            # get public key
            u_pub = keys.get_pubobject(users.users[u_recipient].pub_ser)

            # send message
            users.users[u_recipient].groups[recipient].append((
                username,
                keys.get_encrypted(contents["message"], u_pub),
            ))
    else: # just send normally without groups

        # check if recipient is blocked or blocked by recipient
        if recipient in users.blocks[username]:
            return BLOCKED_BY_RECIPIENT
        if username in users.blocks[recipient]:
            return ALREADY_BLOCKED
    
        # get public keys of recipient and sender
        s_pub = keys.get_pubobject(users.users[username].pub_ser)
        r_pub = keys.get_pubobject(users.users[recipient].pub_ser)

        # check if both not mutual contacts
        if not recipient in users.users[username].contacts:
            users.users[username].contacts[recipient] = []
        if not username in users.users[recipient].contacts:
            users.users[recipient].contacts[username] = []
        
        # send to sender and recipient
        users.users[username].contacts[recipient].append((
            True, # yes, sender sent this message
            keys.get_encrypted(contents["message"], s_pub),
        ))
        users.users[recipient].contacts[username].append((
            False, # no, recipient didnt send this message
            keys.get_encrypted(contents["message"], r_pub),
        ))
        
    return {
        "code": 200,
        "data": True,
    }

@app.route("/join_group", methods=["POST"])
def join_group():
    
    contents = request.get_json()
    if not verify_form(contents, JOIN_GROUP_FORM):
        return MALFORMED_DICT
    username = contents["username"]
    groupname = contents["groupname"]

    # check if groupname is valid or too long
    if len(groupname) > GROUPNAME_MAX: return TOO_MANY_CHARACTERS
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
    users.users[username].groups[groupname] = []
    return {
        "code": 200,
        "data": True,
    }

@app.route("/logout", methods=["POST"])
def logout():

    contents = request.get_json()
    if not verify_form(contents, LOGOUT_FORM):
        return MALFORMED_DICT
    username = contents["username"]

    # delete from user dict and all groups
    for group in users.users[username].groups:
        users.groups[group].remove(username)
    del users.users[username]
    del users.blocks[username]

    return {
        "code": 200,
        "data": True,
    }

@app.route("/leave_group", methods=["POST"])
def leave_group():

    contents = request.get_json()
    if not verify_form(contents, LEAVE_GROUP_FORM):
        return MALFORMED_DICT
    username = contents["username"]
    groupname = contents["groupname"]

    # check if user isnt in group
    if (not groupname in users.users[username].groups) or (groupname not in users.groups):
        return INVALID_GROUP

    # leave group
    users.groups[groupname].remove(username)
    del users.users[username].groups[groupname]

    return {
        "code": 200,
        "data": True,
    }

@app.route("/block_user", methods=["POST"])
def block_user():

    contents = request.get_json()
    if not verify_form(contents, BLOCK_FORM):
        return MALFORMED_DICT
    username = contents["username"]
    blocked = contents["blocked"]

    # check if blocked does not exist
    if not blocked in users.users:
        return NONEXISTENT_RECIPIENT

    # check if already blocked
    if blocked in users.users[username].blocked:
        return ALREADY_BLOCKED

    # block user, remove from contacts
    users.users[username].blocked.add(blocked)
    users.blocks[blocked].add(username)
    users.users[username].contacts.pop(blocked, None)

    return {
        "code": 200,
        "data": True,
    }

@app.route("/unblock_user", methods=["POST"])
def unblock_user():

    contents = request.get_json()
    if not verify_form(contents, UNBLOCK_FORM):
        return MALFORMED_DICT
    username = contents["username"]
    blocked = contents["blocked"]

    # check if blocked
    if not blocked in users.users:
        return NONEXISTENT_RECIPIENT

    # check if already blocked
    if not blocked in users.users[username].blocked:
        return NOT_BLOCKED

    # block user
    users.users[username].blocked.remove(blocked)
    users.blocks[blocked].remove(username)

    return {
        "code": 200,
        "data": True,
    }

@app.route("/retrieve_contacts", methods=["POST"])
def retrieve_contacts():

    contents = request.get_json()
    if not verify_form(contents, RETRIEVE_CONTACTS_FORM):
        return MALFORMED_DICT
    username = contents["username"]

    # get all contacts and return
    # bool is true if is group, else false
    contacts: List[Tuple[str, bool]] = [
        *[(dm, False) for dm in users.users[username].contacts],
        *[(group, True) for group in users.users[username].groups],
    ]
    return {
        "code": 200,
        "data": contacts
    }

@app.route("/group_members", methods=["POST"])
def group_members():

    contents = request.get_json()
    if not verify_form(contents, GROUP_MEMBERS_FORM):
        return MALFORMED_DICT
    username = contents["username"]
    groupname = contents["groupname"]

    # check if user isnt in group
    if (not groupname in users.users[username].groups) or (groupname not in users.groups):
        return INVALID_GROUP

    # return group members
    return {
        "code": 200,
        "data": list(users.groups[groupname])
    }

app.run(host="0.0.0.0", port="5000") # when deploying on pythonanywhere, remove this, and force https