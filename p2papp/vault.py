import json
import os
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from . import keys

VAULT_DIR = Path.home() / '.guildvault'
VAULT_FILE = VAULT_DIR / 'seed_vault.enc'
SALT = b'guild-salt'


def _derive_key(passphrase: bytes) -> bytes:
    return HKDF(algorithm=SHA256(), length=32, salt=None, info=b'vault').derive(passphrase)


def create_vault(passphrase: bytes, phone_mac: str, phone_pub: str, bio_sig: str, geo: str) -> dict:
    VAULT_DIR.mkdir(exist_ok=True)
    priv_bytes, pub_bytes = keys.generate_key_bytes(passphrase)
    btc_seed = os.urandom(32).hex()
    eth_seed = os.urandom(32).hex()
    mac_token = keys.mac_token(phone_mac)
    data = {
        'priv_key': priv_bytes.decode(),
        'pub_key': pub_bytes.decode(),
        'btc_seed': btc_seed,
        'eth_seed': eth_seed,
        'mac_token': mac_token,
        'phone_pub': phone_pub,
        'bio_sig': bio_sig,
        'geo': geo,
    }
    aes = AESGCM(_derive_key(passphrase))
    nonce = os.urandom(12)
    ct = aes.encrypt(nonce, json.dumps(data).encode(), None)
    VAULT_FILE.write_bytes(nonce + ct)
    return data


def save_vault(passphrase: bytes, data: dict) -> None:
    aes = AESGCM(_derive_key(passphrase))
    nonce = os.urandom(12)
    ct = aes.encrypt(nonce, json.dumps(data).encode(), None)
    VAULT_FILE.write_bytes(nonce + ct)


def load_vault(passphrase: bytes) -> dict:
    data = VAULT_FILE.read_bytes()
    aes = AESGCM(_derive_key(passphrase))
    nonce, ct = data[:12], data[12:]
    decoded = aes.decrypt(nonce, ct, None)
    return json.loads(decoded.decode())


def get_wallet_seeds(passphrase: bytes) -> tuple[str, str]:
    data = load_vault(passphrase)
    return data['btc_seed'], data['eth_seed']
