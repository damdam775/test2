import os
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization, hashes
from hashlib import sha256

KEY_DIR = Path(__file__).resolve().parent / 'data'
PRIVATE_KEY_FILE = KEY_DIR / 'private_key.pem'
PUBLIC_KEY_FILE = KEY_DIR / 'public_key.pem'


def generate_keys(passphrase: bytes | None = None) -> None:
    """Generate an Ed25519 key pair and store it with restrictive permissions."""
    KEY_DIR.mkdir(exist_ok=True)
    private_key = ed25519.Ed25519PrivateKey.generate()
    priv_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(passphrase) if passphrase else serialization.NoEncryption(),
    )
    pub_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    PRIVATE_KEY_FILE.write_bytes(priv_bytes)
    os.chmod(PRIVATE_KEY_FILE, 0o600)
    PUBLIC_KEY_FILE.write_bytes(pub_bytes)


def load_private_key(passphrase: bytes | None = None):
    data = PRIVATE_KEY_FILE.read_bytes()
    return serialization.load_pem_private_key(data, password=passphrase)


def load_public_key():
    data = PUBLIC_KEY_FILE.read_bytes()
    return serialization.load_pem_public_key(data)


def generate_key_bytes(passphrase: bytes | None = None) -> tuple[bytes, bytes]:
    """Return a new keypair serialized to PEM format."""
    private_key = ed25519.Ed25519PrivateKey.generate()
    priv_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(passphrase)
        if passphrase
        else serialization.NoEncryption(),
    )
    pub_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return priv_bytes, pub_bytes


def load_private_key_from_bytes(data: bytes, passphrase: bytes | None = None):
    return serialization.load_pem_private_key(data, password=passphrase)


def mac_token(mac: str) -> str:
    """Generate a salted MAC-ID token."""
    digest = sha256()
    digest.update(mac.encode())
    digest.update(b'guild-salt')
    return digest.hexdigest()
