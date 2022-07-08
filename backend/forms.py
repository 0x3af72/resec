REGISTER_FORM = {"username": str}
VERIFICATION_CODE_FORM = {"username": str}
RETRIEVE_MESSAGES_FORM = {"username": str, "verification": str}
SEND_MESSAGE_FORM = {
    "username": str, "verification": str, "recipient": str,
    "group": bool, "message": str,
}
JOIN_GROUP_FORM = {"username": str, "verification": str, "groupname": str}
LOGOUT_FORM = {"username": str, "verification": str}
LEAVE_GROUP_FORM = {"username": str, "verification": str, "groupname": str}