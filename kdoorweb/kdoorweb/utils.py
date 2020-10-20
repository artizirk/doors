import secrets
import base64
import hashlib
from functools import partial

api_key_hash = partial(hashlib.scrypt, n=16384, r=8, p=1)


def gen_new_api_key():
    key = secrets.token_urlsafe()
    salt = secrets.token_urlsafe()
    hash = api_key_hash(key.encode(), salt=salt.encode())
    hash_line = f"{base64.urlsafe_b64encode(hash).decode()}:{salt}"
    return key, hash_line


def check_api_key(key, hash_line):
    stored_hash, salt = hash_line.split(":")
    calculated_hash = api_key_hash(key.encode(), salt=salt.encode())
    return base64.urlsafe_b64encode(calculated_hash).decode() == stored_hash


if __name__ == "__main__":
    key, hash_line = gen_new_api_key()
    print("Key:", key)
    print("hash_line:",  hash_line)
    print("check:", check_api_key(key, hash_line))
