# Secure P2P Demo

This is a minimal proof-of-concept for a peer-to-peer application that stores
its keys locally and uses end-to-end encryption. The implementation is a
starting point inspired by the requested feature list.

## Requirements

- Python 3.11+
- `cryptography` and `websockets` Python packages

## Usage

Generate keys on first run and start listening for peers:

```bash
python3 -m p2papp.cli serve
```

In another terminal (or device) send a message to the listening peer:

```bash
python3 -m p2papp.cli send ws://localhost:8765 "hello"
```

Keys are stored in `p2papp/data/` and protected by the passphrase entered when
running the commands. This simulates unlocking the private key with biometrics.
