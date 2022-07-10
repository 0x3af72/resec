# verify dictionary contents
def verify_form(contents: dict, form: dict) -> bool:
    for key in form:
        if not (key in contents and isinstance(contents[key], form[key])):
            return False
    return True

# error codes
MALFORMED_DICT = {"code": 400, "error": "ERROR_MALFORMED_DICT"}
INCORRECT_VERIFICATION_CODE = {"code": 400, "error": "ERROR_INCORRECT_VERIFICATION_CODE"}
INVALID_PUBLIC_KEY = {"code": 400, "error": "ERROR_INVALID_PUBLIC_KEY"}
UNAVAILABLE_USERNAME = {"code": 400, "error": "ERROR_UNAVAILABLE_USERNAME"}
INVALID_USERNAME = {"code": 400, "error": "ERROR_INVALID_USERNAME"}
NONEXISTENT_USERNAME = {"code": 400, "error": "ERROR_NONEXISTENT_USERNAME"}
INVALID_GROUP = {"code": 400, "error": "ERROR_INVALID_GROUP"}
NONEXISTENT_RECIPIENT = {"code": 400, "error": "ERROR_NONEXISTENT_RECIPIENT"}
INVALID_REQUEST_TYPE = {"code": 400, "error": "ERROR_INVALID_REQUEST_TYPE"}
ALREADY_IN_GROUP = {"code": 400, "error": "ERROR_ALREADY_IN_GROUP"}
ALREADY_BLOCKED = {"code": 400, "error": "ERROR_ALREADY_BLOCKED"}
BLOCKED_BY_RECIPIENT = {"code": 400, "error": "ERROR_BLOCKED_BY_RECIPIENT"}
NOT_BLOCKED = {"code": 400, "error": "ERROR_NOT_BLOCKED"}
INVALID_CONTACT = {"code": 400, "error": "ERROR_INVALID_CONTACT"}