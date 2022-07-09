import time
import threading
from typing import Dict, List, Tuple, Set
from random import choice
from string import ascii_letters, digits

import keys

FROM_CHARS = ascii_letters + digits
AUTO_RESET_DURATION = 2

# sender struct, whether message coming from group or dm
class SENDER:

    # initialize sender given name and groupname, and bool deciding whether message is from group
    def __init__(self, sender: str, group: bool, groupname: str="") -> None:
        self.sender = sender
        self.group = group
        self.groupname = groupname # can use this when it comes from gorup

# user struct to hold user data
class USER:

    # initialize user given serialized public key
    def __init__(self, pub_ser: bytes) -> None:
        self.pub_ser: bytes = pub_ser
        self.messages: List[Tuple[SENDER, bytes]] = []
        self.groups: Set[str] = set() # efficient way to find groups
        self.next_auto_reset: int = 0 # next auto reset in MINUTES
        self.blocked: Set[str] = set() # users blocked by this user
        self._reset_code()

    def _reset_code(self):
        self.code: str = "".join(choice(FROM_CHARS) for i in range(2048))
        self.code_enc: bytes = keys.get_encrypted(self.code, keys.get_pubobject(self.pub_ser))
        self.next_auto_reset = AUTO_RESET_DURATION

    # verify if it is the actual user trying to receive data
    def verify(self, code: str) -> bool:
        res = code == self.code
        self._reset_code()
        return res

# users are temporary, once the server is restarted all user info is deleted.
# we do not need any passwords to verify users, the client will just receive the private key and thats it
users: Dict[str, USER] = {}

# list of groups, for privacy random characters are advised (kind of like a code)
# values are only list of usernames in the group
groups: Dict[str, Set[str]] = {}

# dict of users blocked by other users
# {"a": ["b", "c"]}: a is blocked by users b and c
blocks: Dict[str, Set[str]] = {}

# thread to constantly reset codes
def auto_reset_thread():
    while True:
        time.sleep(60)
        for user in users:
            user = users[user]
            user.next_auto_reset -= 1
            if user.next_auto_reset == 0:
                user._reset_code()
threading.Thread(target=auto_reset_thread).start()

if __name__ == "__main__": pass

    # check user verification (this is outdated)
    # priv, pub = keys.get_keyobjects() # real keys
    # priv_ser, pub_ser = keys.get_priv(priv), keys.get_pub(pub)

    # fakepriv, fakepub = keys.get_keyobjects() # false keys
    # fakepriv_ser = keys.get_priv(fakepriv)
    # user = USER(pub_ser)
    # print(user.verify(fakepriv_ser))
    # print(user.verify(priv_ser))