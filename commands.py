import globals
from errors import *

__commands_ = {}


def command(name):
    def command_def(func):
        global __commands_
        __commands_[name] = func
        return func

    return command_def


def permission(*param):
    def command_per(func):
        def new_func(*args, **kwargs):
            user = args[0]
            if user.permission < set(param):
                return func(*args, **kwargs)
            else:
                raise PermissionError(*[per for per in param if per not in user.permission])
        return new_func
    return command_per


@command("connect")
def connect(socket, username, x, y):
    if len([user for user in globals.users if user.username == username]):
        raise UsernameTakenError(username)
    else:
        globals.users.append()


@permission('room', 'controller')
@command('mv-snake')
def move_snake(user, direction):
    pass
