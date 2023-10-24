import hashlib


async def generate_hash(auth_key: str) -> str:

    auth_key_bytes = auth_key.encode('utf-8')

    return hashlib.sha256(auth_key_bytes).hexdigest()

