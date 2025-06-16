import argparse
import asyncio
from getpass import getpass
from .node import P2PNode
from . import keys, wallet, storage, vault, ledger


def main():
    parser = argparse.ArgumentParser(description="Simple P2P App")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("serve")

    send = sub.add_parser("send")
    send.add_argument("uri")
    send.add_argument("message")

    pair = sub.add_parser("pair")
    pair.add_argument("phone_mac")
    pair.add_argument("phone_pub")

    wgen = sub.add_parser("wallet")
    wgen.add_argument("action", choices=["create", "show"])

    addt = sub.add_parser("addtask")
    addt.add_argument("title")
    addt.add_argument("description")
    addt.add_argument("reward")
    addt.add_argument("radius", type=int)

    sub.add_parser("listtasks")

    args = parser.parse_args()

    passphrase_in = getpass("Biometric unlock: ")
    passphrase = passphrase_in.encode()

    if args.cmd == "pair":
        mac_token = keys.mac_token(args.phone_mac)
        if ledger.has_mac_token(mac_token):
            print("Device already registered in ledger")
            return
        bio_sig = input("Speak phrase (simulate): ")
        geo = input("City: ")
        data = vault.create_vault(passphrase, args.phone_mac, args.phone_pub, bio_sig, geo)
        priv = keys.load_private_key_from_bytes(data['priv_key'].encode(), passphrase)
        ledger.append_registration(priv, {
            'mac_token': data['mac_token'],
            'phone_pub': data['phone_pub'],
            'bio_sig': data['bio_sig'],
            'geo': data['geo'],
        })
        print("Paired and registered")
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
