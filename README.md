# Secure P2P Demo

This repo contains a tiny prototype of a privacy first peer to peer app.  It
includes a command line interface demonstrating phone pairing, encrypted
messaging and a local bounty board.  The code uses an ephemeral X25519 handshake
with AES‑GCM for all traffic.  Private keys and optional wallet seeds are stored
locally and can be protected with a passphrase which represents the biometric
check on the phone.

## Requirements

* Python 3.11+
* `cryptography` and `websockets`

Install dependencies with:

```bash
pip install cryptography websockets
```

## Usage

### Pair devices

Generate a key pair the first time you run the app:

```bash
python3 -m p2papp.cli pair
```

### Run a node

Start the local server:

```bash
python3 -m p2papp.cli serve
```

Send an encrypted message from another terminal or machine:

```bash
python3 -m p2papp.cli send ws://HOST:8765 "hello"
```

### Wallet

Create wallet seeds (shown once and stored encrypted):

```bash
python3 -m p2papp.cli wallet create
```

View stored seeds later with `wallet show`.

### Tasks

Add a local bounty/task:

```bash
python3 -m p2papp.cli addtask "Fix bug" "Need help" 1ETH 5
```

List stored tasks:

```bash
python3 -m p2papp.cli listtasks
```

All task data is stored locally in `p2papp/data/` encrypted at rest.  This keeps
private details on your device while still enabling peer discovery when the node
is extended to broadcast listings.

## Project Overview

* **Peer to peer mesh** – every instance can act as client and server.
* **End to end encryption** – Noise‑like handshake using X25519 and AES‑GCM.
* **Phone pairing** – keys live locally and are unlocked via passphrase.
* **Self custody wallets** – optional Bitcoin and Ethereum seeds stored
  encrypted.
* **Local discovery board** – tasks are saved locally and can later be shared
  with nearby peers.

The current code is intentionally small but forms the basis of the larger design
outlined in the project description.
