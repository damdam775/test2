import os
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

DATA_DIR = Path(__file__).resolve().parent / 'data'
WALLET_FILE = DATA_DIR / 'wallet.json.enc'


def _derive_key(passphrase: bytes) -> bytes:
    return HKDF(algorithm=SHA256(), length=32, salt=None, info=b'wallet').derive(passphrase)


def generate_wallet(passphrase: bytes | None = None) -> tuple[str, str]:
    """Generate Bitcoin and Ethereum seeds and store them encrypted."""
    DATA_DIR.mkdir(exist_ok=True)
    btc_seed = os.urandom(32).hex()
    eth_seed = os.urandom(32).hex()
    if passphrase:
        key = _derive_key(passphrase)
        aes = AESGCM(key)
        nonce = os.urandom(12)
        data = f'{btc_seed}:{eth_seed}'.encode()
        ct = aes.encrypt(nonce, data, None)
        WALLET_FILE.write_bytes(nonce + ct)
    else:
        WALLET_FILE.write_text(f'{btc_seed}:{eth_seed}')
    return btc_seed, eth_seed


def load_wallet(passphrase: bytes | None = None) -> tuple[str, str]:
    data = WALLET_FILE.read_bytes()
    if passphrase:
        key = _derive_key(passphrase)
        aes = AESGCM(key)
        nonce, ct = data[:12], data[12:]
        decoded = aes.decrypt(nonce, ct, None).decode()
    else:
        decoded = data.decode()
    btc, eth = decoded.split(':')
    return btc, eth
