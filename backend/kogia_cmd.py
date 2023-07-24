import argparse
import getpass

from backend.lib.db import ArangoConnection, ArangoConnectionFactory
from backend.lib.config import load_config
from backend.auth.db import DBAuth
from backend.auth import ROLES

def main():
    config = load_config("./config.json")

    db_factory = ArangoConnectionFactory(
        config['kogia']['db_host'], 
        config['kogia']['db_port'], 
        config['kogia']['db_user'], 
        config['kogia']['db_password'],
        config['kogia']['db_name']
    )

    db = db_factory.new()

    parser = argparse.ArgumentParser('Kogia maintenance commands')
    subparsers = parser.add_subparsers(dest="command")

    adduser_parser = subparsers.add_parser("adduser")

    adduser_parser.add_argument('--username', "-u", help="Set username")
    adduser_parser.add_argument('--password', "-p", help="Set password")
    adduser_parser.add_argument('--role', action='append', choices=ROLES)

    args = parser.parse_args()

    if args.command is None:
        print(adduser_parser.format_help())
    elif args.command == "adduser":
        username = args.username
        if username is None:
            username = input("Username> ")
        password = args.password
        if password is None:
            password = getpass.getpass("Password> ")
        auth = DBAuth(db)

        if args.role is None or len(args.role) <= 0: 
            print(f"ERROR: Add at least one from from: {ROLES}")
            return 1
        auth.insert_user(username, password, args.role)
        print(f"User {username} added")
        


if __name__ == '__main__':
    main()