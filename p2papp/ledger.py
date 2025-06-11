import json
import time
from hashlib import sha256
from pathlib import Path
from . import keys

LEDGER_FILE = Path.home() / '.guildvault' / 'ledger.json'


def load_ledger() -> list:
    if not LEDGER_FILE.exists():
        return []
    return json.loads(LEDGER_FILE.read_text())


def save_ledger(chain: list) -> None:
    LEDGER_FILE.parent.mkdir(exist_ok=True)
    LEDGER_FILE.write_text(json.dumps(chain, indent=2))


def block_hash(block: dict) -> str:
    return sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()


def append_registration(priv_key, data: dict) -> None:
    chain = load_ledger()
    index = len(chain)
    prev_hash = block_hash(chain[-1]) if chain else 'genesis'
    body = {
        'index': index,
        'prev_hash': prev_hash,
        'timestamp': time.time(),
        'data': data,
    }
    signature = priv_key.sign(json.dumps(body, sort_keys=True).encode()).hex()
    body['signature'] = signature
    chain.append(body)
    save_ledger(chain)


def has_mac_token(token: str) -> bool:
    return any(b['data'].get('mac_token') == token for b in load_ledger())
