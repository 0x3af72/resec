####################################################################################
#
# Written by cry6.
# This is an exact copy of the keys.py used in the backend.
#
####################################################################################

from typing import Tuple

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization

KEYSIZE = 4096

# magic numbers...
ECHUNKSIZE = 446 # encryption
DCHUNKSIZE = 512 # decryption

# generate key objects
def get_keyobjects(KSIZE: int=KEYSIZE) -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
    priv = rsa.generate_private_key(
        public_exponent=65537,
        key_size=KSIZE,
        backend=default_backend(),
    )
    pub = priv.public_key()
    return priv, pub

# get bytes representation of public key
def get_pub(pub: rsa.RSAPublicKey) -> bytes:
    serial = pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return serial

# get bytes representation of private key
def get_priv(priv: rsa.RSAPrivateKey) -> bytes:
    serial = priv.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return serial

# get public key from bytes representation
def get_pubobject(serial: bytes) -> rsa.RSAPublicKey:
    pub = serialization.load_pem_public_key(
        serial, backend=default_backend(),
    )
    return pub

# get private key from bytes representation
def get_privobject(serial: bytes) -> rsa.RSAPrivateKey:
    priv = serialization.load_pem_private_key(
        serial, password=None, backend=default_backend(),
    )
    return priv

# encrypt text with public key
def get_encrypted(text: str, pub: rsa.RSAPublicKey) -> bytes:
    enc: bytes = b""
    while text:
        enc += pub.encrypt(
            text[:ECHUNKSIZE].encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            )
        )
        text = text[ECHUNKSIZE:]
    return enc

# decrypt encrypted text with private key
def get_decrypted(enc: bytes, priv: rsa.RSAPrivateKey) -> str:
    dec: str = ""
    while enc:
        dec += priv.decrypt(
            enc[:DCHUNKSIZE],
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            )
        ).decode()
        enc = enc[DCHUNKSIZE:]
    return dec

if __name__ == "__main__":

    # check key creation and serialization
    priv, pub = get_keyobjects()
    # print(get_pub(pub))
    # print(get_priv(priv))

    # check getting keys from bytes
    priv = get_privobject(get_priv(priv))
    pub = get_pubobject(get_pub(pub))

    # check encryption and decryption
    enc = get_encrypted("HELLOHJAHJA", pub)
    print(len(enc))
    dec = get_decrypted(enc, priv)
    print(dec)

    # ser to string to key
    # pub_ser_str = get_pub(pub).decode()
    # pub_ser = pub_ser_str.encode()
    # pub_2 = get_pubobject(pub_ser)

    # priv_ser_str = get_priv(priv).decode()
    # priv_ser = priv_ser_str.encode()
    # priv_2 = get_privobject(priv_ser)
    # print(get_decrypted(enc, priv_2))