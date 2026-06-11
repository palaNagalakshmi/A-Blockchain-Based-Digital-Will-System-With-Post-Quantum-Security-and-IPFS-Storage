import hashlib
from pqcrypto.sign.falcon_512 import verify


def hash_file(file_path):

    sha = hashlib.sha256()

    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            sha.update(chunk)

    return sha.digest()


def pq_verify_file(file_path, public_key, signature):

    file_hash = hash_file(file_path)

    try:
        verify(public_key, file_hash, signature)
        return True
    except Exception:
        return False