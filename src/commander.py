import globals
from errors import *
from globals import User

__commands__ = {}


def execute_command(user, *info):
	if info[0] not in __commands__.keys():
		raise NoSuchCommand(info[0])
	current_command = __commands__[info[0]]

	if len(info) != len(current_command):
		raise WrongNumberOfArguments(info[0], len(current_command) - 1, len(info) - 1)

	params = [user]

	for i in xrange(1, len(info)):
		params.append(current_command[i](info[i]))

	current_command[0](*params)


def command(name, *types):
	def command_def(func):
		global __commands__
		__commands__[name] = (func,) + types
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


@command("connect", str, int, int)
def connect(socket, username, x, y):
	if len([user for user in globals.users if user.username == username]):
		raise UsernameTakenError(username)
	else:
		user = User(username, socket, x, y)
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
@command('mv-snake', str)
def move_snake(user, direction):
	pass
