import asyncio
import json
import os
from websockets import serve
from websockets.client import connect
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from . import keys


class P2PNode:
    def __init__(self, nickname: str, passphrase: bytes | None = None):
        self.nickname = nickname
        if not keys.PRIVATE_KEY_FILE.exists():
            keys.generate_keys(passphrase)
        self.private_key: Ed25519PrivateKey = keys.load_private_key(passphrase)
        self.public_key = self.private_key.public_key()

    async def handler(self, websocket):
        await self.perform_handshake(websocket, initiator=False)
        async for raw in websocket:
            nonce_hex, ct_hex = raw.split(":", 1)
            plaintext = self.aesgcm.decrypt(bytes.fromhex(nonce_hex), bytes.fromhex(ct_hex), None)
            data = json.loads(plaintext.decode())
            print(f"Received: {data}")

    async def start_server(self, host="0.0.0.0", port=8765):
        async with serve(self.handler, host, port):
            print(f"Listening on {host}:{port}")
            await asyncio.Future()

    async def connect_and_send(self, uri: str, payload: dict):
        async with connect(uri) as websocket:
            await self.perform_handshake(websocket, initiator=True)
            plaintext = json.dumps(payload).encode()
            nonce = os.urandom(12)
            ct = self.aesgcm.encrypt(nonce, plaintext, None)
            await websocket.send(f"{nonce.hex()}:{ct.hex()}")

    async def perform_handshake(self, websocket, initiator: bool):
        """Establish a shared AES key using an ephemeral X25519 exchange."""
        my_identity = self.public_key.public_bytes(
            serialization.Encoding.Raw,
            serialization.PublicFormat.Raw,
        )
        eph_priv = x25519.X25519PrivateKey.generate()
        eph_pub = eph_priv.public_key().public_bytes(
            serialization.Encoding.Raw,
            serialization.PublicFormat.Raw,
        )
        if initiator:
            await websocket.send(json.dumps({"id": my_identity.hex(), "eph": eph_pub.hex()}))
            msg = json.loads(await websocket.recv())
        else:
            msg = json.loads(await websocket.recv())
            await websocket.send(json.dumps({"id": my_identity.hex(), "eph": eph_pub.hex()}))

        peer_id = bytes.fromhex(msg["id"])
        peer_eph = x25519.X25519PublicKey.from_public_bytes(bytes.fromhex(msg["eph"]))
        shared = eph_priv.exchange(peer_eph)

        hkdf = HKDF(algorithm=SHA256(), length=32, salt=None, info=b"p2p")
        key = hkdf.derive(shared)
        self.aesgcm = AESGCM(key)
        self.peer_id = peer_id
