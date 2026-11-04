import base64
import hashlib
import hmac
import os

# Work factors for scrypt. Raising them only affects newly stored passwords,
# because each stored value records the ones it was made with.
SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1


def _scrypt(password: str, salt: bytes, n: int, r: int, p: int) -> bytes:
    return hashlib.scrypt(password.encode(), salt=salt, n=n, r=r, p=p)


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = _scrypt(password, salt, SCRYPT_N, SCRYPT_R, SCRYPT_P)
    encoded_salt = base64.b64encode(salt).decode()
    encoded_digest = base64.b64encode(digest).decode()
    return f"scrypt${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}${encoded_salt}${encoded_digest}"


def verify_password(password: str, stored: str) -> bool:
    _, n, r, p, encoded_salt, encoded_digest = stored.split("$")
    digest = _scrypt(password, base64.b64decode(encoded_salt), int(n), int(r), int(p))
    return hmac.compare_digest(digest, base64.b64decode(encoded_digest))
