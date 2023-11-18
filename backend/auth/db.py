import os
import hashlib 
import secrets
import time

from backend.lib.db import ArangoConnection

TIMEOUT = 60 * 60 * 2

class DBAuth():

    def __init__(self, db : ArangoConnection) -> None:
        self._db = db

    def authenticate_new(self, username, credential):
        user_data = self._db.get_by_match('users', '_key', username)
        if user_data is None:
            return False, "Authentication failed", []
        if "." not in user_data['password']:
            return False, "User entry is corrupted", []
        salt = bytes.fromhex(user_data['password'].split(".")[0])
        hashed_password = self._hash_password(credential, salt)

        if hashed_password == user_data['password']:
            api_token = secrets.token_hex(48)
            self._db.insert("sessions", {
                "_key": api_token,
                "username": username,
                "expire": int(time.time()) + TIMEOUT,
                "roles": user_data['roles']
            })
            return True, api_token, user_data['roles']
        else:
            return False, "Authentication failed", []
    
    def authenticate_existing(self, key):
        session_data = self._db.get_by_match('sessions', '_key', key)
        if session_data is None:
            return False, "Unauthenticated", []
        else:
            return True, session_data['username'], session_data['roles']

    def authorize(self, username, route):
        return False, "No authorization yet"
    
    def remove_session(self, key):
        session_data = self._db.get_by_match('sessions', '_key', key)
        if session_data is None:
            return False, "Session not found"
        else:
            self._db.delete('sessions', {"_key": key})
            return True, ""
    
    def _hash_password(self, password, salt):
        hashed_password = hashlib.scrypt(password=password.encode(), salt=salt, n=2048, r=8, p=1)
        return salt.hex() + "." + hashed_password.hex()
    
    def insert_user(self, username, password, roles):
        salt = os.urandom(32)
        hashed_pass = self._hash_password(password, salt)
        self._db.insert('users', {
            "_key": username,
            "password": hashed_pass,
            "roles": roles
        })