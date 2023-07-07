

class DBAuth():

    def __init__(self) -> None:
        pass

    def authenticate_new(self, username, credential):
        return False, "Not implemented"
    
    def authenticate_existing(self, key):
        return False, "Not implemented"

    def authorize(self, username, route):
        return False, "No authorization yet"