class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.authenticated = False

    def authenticate(self, username, password):
        self.authenticated = (self.username == username and self.password == password)
        return self.authenticated