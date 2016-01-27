import globals
from globals import User, Room
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
        user = User(username, socket, int(x), int(y))
        globals.users.append(user)


def join_room(user, room_name, password):
    """

    :type user: global.User
    :param room_name:
    :param password:
    :return:
    """
    room = next(r for r in globals.rooms if r.name == room_name)
    if room.password is not None and room.password == password:
        pass
        # TODO: finish this method


@permission('room', 'controller')
@command('mv-snake')
def move_snake(user, direction):
    pass
