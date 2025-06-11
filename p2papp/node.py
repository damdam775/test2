import asyncio
import json
from pathlib import Path
from websockets import serve
from websockets.client import connect
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.hashes import Hash, SHA256
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
        async for message in websocket:
            data = json.loads(message)
            print(f"Received: {data}")

    async def start_server(self, host='0.0.0.0', port=8765):
        async with serve(self.handler, host, port):
            print(f"Listening on {host}:{port}")
            await asyncio.Future()

    async def connect_and_send(self, uri: str, payload: dict):
        async with connect(uri) as websocket:
            await self.perform_handshake(websocket, initiator=True)
            await websocket.send(json.dumps(payload))

    async def perform_handshake(self, websocket, initiator: bool):
        # exchange public keys
        my_pub = self.public_key.public_bytes(
            serialization.Encoding.Raw,
            serialization.PublicFormat.Raw,
        )
        if initiator:
            await websocket.send(my_pub.hex())
            peer_pub_hex = await websocket.recv()
        else:
            peer_pub_hex = await websocket.recv()
            await websocket.send(my_pub.hex())
        peer_pub = bytes.fromhex(peer_pub_hex)
        # derive session key using hash(my_pub + peer_pub)
        digest = Hash(SHA256())
        if initiator:
            digest.update(my_pub + peer_pub)
        else:
            digest.update(peer_pub + my_pub)
        key = digest.finalize()[:32]
        self.aesgcm = AESGCM(key)
