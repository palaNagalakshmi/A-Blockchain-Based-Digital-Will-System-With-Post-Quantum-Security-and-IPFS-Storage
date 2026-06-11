import hashlib
from pqcrypto.sign.falcon_512 import generate_keypair, sign


def hash_file(file_path):
    sha = hashlib.sha256()

    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            sha.update(chunk)

    return sha.digest()


def pq_sign_file(file_path):
    """
    Returns:
        public_key (bytes)
        signature (bytes)
    """
    public_key, secret_key = generate_keypair()

    file_hash = hash_file(file_path)
    signature = sign(secret_key, file_hash)

    return public_key, signature