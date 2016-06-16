from exceptions import TypeError, NameError

class PermissionError(RuntimeError):
    def __init__(self, *per):
        RuntimeError.__init__(self, 'user has no {0} permission'.format(per))


class UsernameTakenError(RuntimeError):
    def __init__(self, username):
        RuntimeError.__init__(self, 'The username \'{0}\' is already taken'.format(username))


class WrongNumberOfArguments(TypeError):
    def __init__(self, name, needed, given):
        TypeError.__init__(self, 'the command \'{0}\' takes exactly {1} argument{3} ({2} given)'.format(name, needed, given,'s' if needed > 1 else ''))



class NoSuchCommand(NameError):
    def __init__(self, name):
        NameError.__init__(self, 'command \'{0}\' is not defined'.format(name))