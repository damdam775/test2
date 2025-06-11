import os
from . import vault


def generate_wallet(passphrase: bytes) -> tuple[str, str]:
    """Generate Bitcoin and Ethereum seeds and store them in the vault."""
    data = vault.load_vault(passphrase)
    btc_seed = os.urandom(32).hex()
    eth_seed = os.urandom(32).hex()
    data['btc_seed'] = btc_seed
    data['eth_seed'] = eth_seed
    vault.save_vault(passphrase, data)
    return btc_seed, eth_seed


def load_wallet(passphrase: bytes) -> tuple[str, str]:
    return vault.get_wallet_seeds(passphrase)
