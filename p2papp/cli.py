import argparse
import asyncio
from getpass import getpass
from .node import P2PNode


def main():
    parser = argparse.ArgumentParser(description="Simple P2P App")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("serve")

    send = sub.add_parser("send")
    send.add_argument("uri")
    send.add_argument("message")

    args = parser.parse_args()
    passphrase = getpass("Unlock key (biometric simulation): ") or None
    node = P2PNode(nickname="anon", passphrase=passphrase.encode() if passphrase else None)

    if args.cmd == "serve":
        asyncio.run(node.start_server())
    elif args.cmd == "send":
        payload = {"msg": args.message}
        asyncio.run(node.connect_and_send(args.uri, payload))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
