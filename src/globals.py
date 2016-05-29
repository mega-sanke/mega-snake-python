from notification import *
import threading
import time

rooms = []
users = []  # type: list[User]


class Slot:
	def __init__(self, *cord):
		from numpy import array as arr
		self.coordinates = arr(cord)

	def __add__(self, other):
		return Slot(*(self.coordinates + other.coordinates))

	def __sub__(self, other):
		return self + (-other)

	def __neg__(self):
		return Slot(*(-self.coordinates))

	def __getitem__(self, item):
		return self.coordinates[item]

	def __setitem__(self, key, value):
		self.coordinates[key] = value

	def __iter__(self):
		return iter(self.coordinates)

	def __str__(self):
		return repr(self.coordinates)[6:-1]

	def __repr__(self):
		return repr(self.coordinates)[6:-1]

	def __len__(self):
		return len(self.coordinates)

	def __eq__(self, other):
		if not isinstance(other, Slot):
			return False
		return all(self.coordinates == other.coordinates)

	def copy(self):
		return Slot(*self.coordinates)

	@staticmethod
	def rand_slot(x, y):
		import random
		new_x = random.randint(0,x-1)
		new_y = random.randint(0, y -1)
		return Slot(new_x, new_y)


class User:
	"""
	This class represent a client of the game.

	Every user has username (unique one), his socket (for communicational reasons) and the dimension of his board.
	"""

	def __init__(self, name, socket, gridx, gridy):

		"""
		Construct new User.

		:param name: The new user's username.
		:param socket: The socket of the user.
		:param gridx: The x size of the user's screen.
		:param gridy: The y size of the user's screen.


		:type name: str
		:type socket: socket.socket
		:type gridy: int
		:type gridx: int
		:return:
		"""
		self.name = name
		self.socket = socket
		self.permissions = set([])
		self.x = gridx
		self.y = gridy
		self.gates = {}
		self.room = None

	def set_room(self, room):

		"""
		The function sets a room for the user

		:param room: The room the user want to join to
		:type room: global.Room
		"""
		self.room = room

	def clear_room(self):
		"""
		The function remove the user from its current room.

		:return:
		:rtype:
		"""
		self.room.users.remove(self)
		self.set_room(None)

	def add_gate(self, id, x, y=None):
		"""
		This function adds new gate to the user board (it followed by notification to the client)

		:param id: The gate's id.
		:type id: int
		:param x: The x value of the new gate
		:type x: int
		:param y: The y value on the new gate
		:type y: int
		"""
		slot = Slot(x, y)
		if y is None:
			slot = x

		slots = {g['slot'] for g in self.gates}
		if slot not in slots:
			self.gates = self.gates | {{'id': id, 'slot': Slot(*slot)}}

		# TODO: add notification

	def add_permission(self, *pers):
		"""
		This function is used to remove permissions from users

		:param pers: The new permissions
		:type pers: list[str]
		"""
		self.permissions = self.permissions | set(pers)

	def remove_permissions(self, *pers):
		"""
		This function is used to remove permissions from users

		:param pers: The permissions we want to remove
		:type pers: list[str]
		"""
		self.permissions = self.permissions - set(pers)

	def __str__(self):
		return 'User {0}'.format(self.name)

	def __repr__(self):
		return str(self)


class Room(threading.Thread):
	"""
    This class represent a Game Room.
    Each Room contain it's password, users, admin, and such on.
    """
	def __init__(self, name, admin, password=None):
		threading.Thread.__init__(self)
		self.name = name
		self.admin = admin
		self.password = password
		self.users = set([])
		self.controller = admin
		self.alive = True
		self.pause = 0.5
		self.moves = []
		self.last_move = '-'
		self.snake = [{'user': self.controller, 'num': 0, 'snake': [Slot(0, 0)]}]
		self.add_user(admin)
		self.rand_food()
		self.start()

	def add_user(self, *new_users):
		self.users = self.users | set(new_users)
		for user in new_users:
			user.set_room(self)
			user.add_permission('room')

	def set_controller(self, user):
		self.controller = user

	def eat_food(self, link):
		maxi = max(instance['num'] for instance in self.snake)
		snake = next(instance['snake'] for instance in self.snake if instance['num'] == maxi)
		last = snake[-1].copy()
		self.__apply_move__(link)
		snake.append(last)
		self.pause = self.pause / 1.2
		self.rand_food()

	def rand_food(self):
		import random
		user = random.choice(tuple(self.users))
		slots = [u['snake'] for u in self.snake if u['user'] == user]
		import itertools
		slots = list(itertools.chain(*slots))

		food = Slot.rand_slot(user.x, user.y)
		while food in slots:
			food = Slot.rand_slot(user.x, user.y)

		self.food_user = user;
		self.food = food;

	def kill(self):
		self.alive = False

	def find_other_user_by_gate(self, gate):
		use = (user for user in self.users if user is not self.controller)
		for user in use:
			for g in user.gates:
				if g['id'] == gate['id']:
					return user, g['slot']

	def __apply_move__(self, link):
		maxi = max(instance['num'] for instance in self.snake)
		snake = next(instance for instance in self.snake if instance['num'] == maxi)
		snake['snake'].pop(-1)
		first_part = next(instance for instance in self.snake if instance['num'] == 0)
		first_part['snake'].insert(0, link)
		if not len(snake['snake']):
			self.snake.remove(snake)

	def __apply_gate__(self, link):
		gate = next(gate for gate in self.controller.gates if gate['slot'] == link)
		user1, slot1 = self.find_other_user_by_gate(gate)
		for instance in self.snake:
			instance['num'] += 1
		notify_variable(self.controller, 'controller', False)
		self.set_controller(user1)
		self.snake.append({'user': user1, 'num': 0, 'snake': [slot1]})

	def get_snake(self, user):
		chains = list(a['snake'] for a in self.snake if a['user'] == user)
		import itertools
		return set(itertools.chain(*chains))

	def clear_empty(self):
		for instance in self.snake:
			if not len(instance['snake']):
				self.snake.remove(instance)

	def move_snake(self, direction):
		if direction == '-':
			return

		link = next(instance['snake'][0] for instance in self.snake if instance['num'] == 0).copy()
		if direction == 'N':
			link[1] -= 1
		elif direction == 'S':
			link[1] += 1
		elif direction == 'W':
			link[0] -= 1
		elif direction == 'E':
			link[0] += 1

		gates_slots = [g['slot'] for g in self.controller.gates]

		print 'link', link
		print 'link', self.food
		print self.food == link
		if self.controller is self.food_user and link == self.food:
			print 'Eat food!!!'
			self.eat_food(link)
		elif link in gates_slots:
			self.__apply_gate__(link)
		elif link[0] < 0 or link[0] >= self.controller.x or link[1] < 0 or link[1] >= self.controller.y or (
					link in [b for b in next(a['snake'] for a in self.snake if a['num'] == 0)]):
			self.kill()
		else:
			self.__apply_move__(link)

		self.clear_empty()

	def step(self):
		move = '-'
		if self.moves:
			move = self.moves.pop(0)
			if not self.moves:
				self.moves.append(move)
		self.move_snake(move)
		length = sum(len(link['snake']) for link in self.snake)
		for user in self.users:
			snake = []
			for s in self.snake:
				if s['user'] is user:
					snake += s['snake']
			notify_variable(user, 'snake', str(snake))
			notify_variable(user, 'alive', self.alive)
			notify_variable(user, 'link-count', length)
			if self.food_user is user:
				notify_variable(user, 'food', str([self.food]))
		notify_variable(self.controller, 'controller', True)

	def add_move(self, direction):
		neg = {'-': '-', 'N': 'S', 'S': 'N', 'W': 'E', 'E': 'W'}
		if not self.moves or not (self.moves[-1] is direction or self.moves[-1] is neg[direction]):
			self.moves.append(direction)

	def __str__(self):
		return 'Room {0}'.format(self.name)

	def __repr__(self):
		return str(self)

	def run(self):
		while self.alive:
			self.step()
			time.sleep(self.pause)
