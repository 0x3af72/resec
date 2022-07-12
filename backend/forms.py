REGISTER_FORM = {"username": str}
VERIFICATION_CODE_FORM = {"username": str}
RETRIEVE_MESSAGES_FORM = {"username": str, "verification": str, "channel": str, "group": bool}
RETRIEVE_CONTACTS_FORM = {"username": str, "verification": str}
JOIN_GROUP_FORM = {"username": str, "verification": str, "groupname": str}
LOGOUT_FORM = {"username": str, "verification": str}
LEAVE_GROUP_FORM = {"username": str, "verification": str, "groupname": str}
BLOCK_FORM = {"username": str, "verification": str, "blocked": str}
UNBLOCK_FORM = {"username": str, "verification": str, "blocked": str}
GROUP_MEMBERS_FORM = {"username": str, "verification": str, "groupname": str}
SEND_MESSAGE_FORM = {
    "username": str, "verification": str, "recipient": str,
    "group": bool, "message": str,
}