import json
import os
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

DATA_DIR = Path(__file__).resolve().parent / 'data'
TASK_FILE = DATA_DIR / 'tasks.json.enc'


def _derive_key(passphrase: bytes) -> bytes:
    return HKDF(algorithm=SHA256(), length=32, salt=None, info=b'tasks').derive(passphrase)


def load_tasks(passphrase: bytes | None = None) -> list[dict]:
    if not TASK_FILE.exists():
        return []
    data = TASK_FILE.read_bytes()
    if passphrase:
        aes = AESGCM(_derive_key(passphrase))
        nonce, ct = data[:12], data[12:]
        content = aes.decrypt(nonce, ct, None)
    else:
        content = data
    return json.loads(content.decode())


def save_tasks(tasks: list[dict], passphrase: bytes | None = None) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    encoded = json.dumps(tasks).encode()
    if passphrase:
        aes = AESGCM(_derive_key(passphrase))
        nonce = os.urandom(12)
        ct = aes.encrypt(nonce, encoded, None)
        TASK_FILE.write_bytes(nonce + ct)
    else:
        TASK_FILE.write_bytes(encoded)


def add_task(title: str, description: str, reward: str, radius: int, passphrase: bytes | None = None) -> None:
    tasks = load_tasks(passphrase)
    tasks.append({
        'title': title,
        'description': description,
        'reward': reward,
        'radius': radius,
    })
    save_tasks(tasks, passphrase)
