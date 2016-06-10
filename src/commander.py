import globals
from errors import *
from globals import User, Room
from notification import *


__commands__ = {}


def execute_command(user, *info):
	info = list(info)
	if info[0] not in __commands__.keys():
		raise NoSuchCommand(info[0])
	current_command = __commands__[info[0]]

	for i in info:
		if i == '':
			info.remove(i)
	if len(info) != len(current_command):
		raise WrongNumberOfArguments(info[0], len(current_command) - 1, len(info) - 1)

	params = [user]

	for i in xrange(1, len(info)):
			params.append(current_command[i](info[i]))
	# print info[0], 'by ', user, 'with ', params[1:]
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
			if user.permissions < set(param) or 'super-admin' in user.permissions:
				return func(*args, **kwargs)
			else:
				raise PermissionError(*[per for per in param if per not in user.permissions])

		return new_func

	return command_per


@command("connect", str, int, int)
def connect(socket, username, x, y):
	if len([user for user in globals.users if user.name == username]):
		raise UsernameTakenError(username)
	else:
		user = User(username, socket, x, y)
		globals.users.append(user)
		user.add_permission('can-exit')
		notify_message(user, 'start')
		for room in globals.rooms:
			notify_variable(user, room.name, True, 'room')


@command('mv-snake', str)
@permission('room', 'controller')
def move_snake(user, direction):
	user.room.add_move(direction)


@command('create-room', str, str)
def add_room(user, name, password):
	if user.has_permission('room'):
		notify_error(user, "Can't create room while connected to other room.")
		return
	if [room for room in globals.rooms if room.name == name]:
		notify_error(user, "Name \'{0}\' is taken.".format(name))
		return
	r = Room(name, user, password)
	globals.rooms.append(r)
	for user in globals.users:
		notify_variable(user, name, True, 'room')

@command('join-room', str, str)
def join_room(user, name, password):
	r = next(r for r in globals.rooms if r.name == name)
	if r.password == password:
		r.add_user(user)
		notify_message(user, 'joined room {0}'.format(name))
	else:
		notify_error(user, 'wrong password')

@command('log-off')
def log_off(user):
	if 'cat-exit' not in user.permissions:
		notify_error(user, 'can\'t quit while the user is the controller')
		return
	globals.users.remove(user)
	user.room.remove_user(user)
	user.socket.close()
	notify_message(user, 'exit')


@command('print')
def p(user):
	print user
	print globals.users
	print globals.rooms



@command('notify')
def notify(user):
	notify_message(user, 'test')


@command('eval', str)
def eva(user, v):
	print eval(v)

@command('exac', str)
def exe(user, v):
	exec(v)
