# verify dictionary contents
def verify_form(contents: dict, form: dict) -> bool:
    for key in form:
        if not (key in contents and isinstance(contents[key], form[key])):
            return False
    return True

# error codes
MALFORMED_DICT = {"code": 400, "error": "ERROR_MALFORMED_DICT"}
INVALID_PUBLIC_KEY = {"code": 400, "error": "ERROR_INVALID_PUBLIC_KEY"}
INVALID_USERNAME = {"code": 400, "error": "ERROR_INVALID_USERNAME"}
INVALID_GROUP = {"code": 400, "error": "ERROR_INVALID_GROUP"}
INVALID_REQUEST_TYPE = {"code": 400, "error": "ERROR_INVALID_REQUEST_TYPE"}
INVALID_CONTACT = {"code": 400, "error": "ERROR_INVALID_CONTACT"}
NONEXISTENT_USERNAME = {"code": 400, "error": "ERROR_NONEXISTENT_USERNAME"}
NONEXISTENT_RECIPIENT = {"code": 400, "error": "ERROR_NONEXISTENT_RECIPIENT"}
ALREADY_IN_GROUP = {"code": 400, "error": "ERROR_ALREADY_IN_GROUP"}
ALREADY_BLOCKED = {"code": 400, "error": "ERROR_ALREADY_BLOCKED"}
NOT_BLOCKED = {"code": 400, "error": "ERROR_NOT_BLOCKED"}
BLOCKED_BY_RECIPIENT = {"code": 400, "error": "ERROR_BLOCKED_BY_RECIPIENT"}
INCORRECT_VERIFICATION_CODE = {"code": 400, "error": "ERROR_INCORRECT_VERIFICATION_CODE"}
UNAVAILABLE_USERNAME = {"code": 400, "error": "ERROR_UNAVAILABLE_USERNAME"}
TOO_MANY_CHARACTERS = {"code": 400, "error": "ERROR_TOO_MANY_CHARACTERS"}
TOO_MANY_HITS = {"code": 400, "error": "ERROR_TOO_MANY_HITS"}