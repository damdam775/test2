import argparse
import asyncio
from getpass import getpass
from .node import P2PNode
from . import keys, wallet, storage


def main():
    parser = argparse.ArgumentParser(description="Simple P2P App")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("serve")

    send = sub.add_parser("send")
    send.add_argument("uri")
    send.add_argument("message")

    sub.add_parser("pair")

    wgen = sub.add_parser("wallet")
    wgen.add_argument("action", choices=["create", "show"])

    addt = sub.add_parser("addtask")
    addt.add_argument("title")
    addt.add_argument("description")
    addt.add_argument("reward")
    addt.add_argument("radius", type=int)

    sub.add_parser("listtasks")

    args = parser.parse_args()

    passphrase_in = getpass("Biometric unlock: ") or None
    passphrase = passphrase_in.encode() if passphrase_in else None

    if args.cmd == "pair":
        keys.generate_keys(passphrase)
        print("Keys generated")
        return

    node = P2PNode(nickname="anon", passphrase=passphrase)

    if args.cmd == "serve":
        asyncio.run(node.start_server())
    elif args.cmd == "send":
        payload = {"msg": args.message}
        asyncio.run(node.connect_and_send(args.uri, payload))
    elif args.cmd == "wallet":
        if args.action == "create":
            btc, eth = wallet.generate_wallet(passphrase)
            print("Bitcoin seed:", btc)
            print("Ethereum seed:", eth)
        else:
            btc, eth = wallet.load_wallet(passphrase)
            print("Bitcoin seed:", btc)
            print("Ethereum seed:", eth)
    elif args.cmd == "addtask":
        storage.add_task(args.title, args.description, args.reward, args.radius, passphrase)
        print("Task saved")
    elif args.cmd == "listtasks":
        tasks = storage.load_tasks(passphrase)
        for t in tasks:
            print(f"{t['title']} - {t['reward']} within {t['radius']}km")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
