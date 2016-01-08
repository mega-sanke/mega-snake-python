class PermissionError(RuntimeError):
    def __init__(self, *per):
        RuntimeError.__init__(self, 'user has no {0} permission'.format(self.per))


class UsernameTakenError(RuntimeError):
    def __init__(self, username):
        RuntimeError.__init__(self, 'The username \'{0}\' is already taken'.format(username))

