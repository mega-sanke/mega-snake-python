from notification import *
import threading
import time

NEG = {'-': '-', 'N': 'S', 'S': 'N', 'W': 'E', 'E': 'W'}

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
		new_x = random.randint(0, x - 1)
		new_y = random.randint(0, y - 1)
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
		self.neighbours = {'N': False, 'S': False, 'W': False, 'E': False}
		self.x = gridx
		self.y = gridy
		self.gates = []
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
		self.remove_permission('room')
		self.remove_permission('controller')
		self.neighbours = {'N': False, 'S': False, 'W': False, 'E': False}

		notify_variable(self, 'snake', str([]), 'slots')
		notify_variable(self, 'alive', False, 'boolean')
		notify_variable(self, 'link-count', 0, 'number')
		notify_variable(self, 'gates', str([]), 'slots')
		notify_variable(self, 'food', str([]), 'slots')
		notify_variable(self, 'controller', False, 'boolean')

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

		slots = [g['slot'] for g in self.gates]
		if slot not in slots:
			self.gates.append({'id': id, 'slot': Slot(*slot)})

	def add_permission(self, *pers):
		"""
		This function is used to remove permissions from users

		:param pers: The new permissions
		:type pers: list[str]
		"""
		self.permissions = self.permissions | set(pers)

	def remove_permission(self, *pers):
		"""
		This function is used to remove permissions from users

		:param pers: The permissions we want to remove
		:type pers: list[str]
		"""
		self.permissions = self.permissions - set(pers)

	def has_permission(self, p):
		return p in self.permissions

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
		self.controller.add_permission('controller')
		self.controller.remove_permission('can-exit')
		self.alive = True
		self.pause = 0.5
		self.moves = []
		self.last_move = '-'
		self.gate_id = 0
		self.snake = [{'user': self.controller, 'num': 0, 'snake': [Slot(0, 0)]}]
		self.food_user = []
		self.gates = dict()
		self.add_user(admin)
		self.rand_food()
		self.start()

	def remove_user(self, user):
		"""

		:param user:
		:type user: User
		:return:
		:rtype:
		"""


		linked_users = [user.neighbours[wind][1] for wind in user.neighbours if user.neighbours[wind]]
		ids = {gate['id'] for gate in self.gates[user]}
		del self.gates[user]
		for still_user in linked_users:
			for gate in self.gates[still_user]:
				if gate['id'] in ids:
					self.gates[still_user].remove(gate)
		user.clear_room()
		user.add_permission('can-exit')



	def add_user(self, *new_users):
		if not self.users:
			self.users = self.users | set(new_users)
			for user in new_users:
				self.gates[user] = []
				user.set_room(self)
				user.add_permission('room')
			return

		import random
		for user in new_users:
			self.gates[user] = []

			free_users = {user for user in self.users if [key for key in user.neighbours if not user.neighbours[key]]}
			new_neighbour = random.choice(list(free_users))
			neighbour_dir = random.choice(
				[key for key in new_neighbour.neighbours if not new_neighbour.neighbours[key]])
			user_dir = NEG[neighbour_dir]
			new_neighbour.neighbours[neighbour_dir] = (True, user)
			user.neighbours[user_dir] = (True, new_neighbour)

			size = min(user.x if user_dir in {'N', 'W'} else user.y,
					   new_neighbour.x if neighbour_dir in {'N', 'W'} else new_neighbour.y)

			if user_dir is 'N':
				for i in xrange(size):
					self.add_gate(user, self.gate_id, i, 0)
					self.add_gate(new_neighbour, self.gate_id, i, new_neighbour.y - 1)
					self.gate_id += 1
			elif user_dir is 'S':
				for i in xrange(size):
					self.add_gate(user, self.gate_id, i, user.y - 1)
					self.add_gate(new_neighbour, self.gate_id, i, 0)
					self.gate_id += 1
			elif user_dir is 'E':
				for i in xrange(size):
					self.add_gate(user, self.gate_id, user.x - 1, i)
					self.add_gate(new_neighbour, self.gate_id, 0, i)
					self.gate_id += 1
			elif user_dir is 'W':
				for i in xrange(size):
					self.add_gate(user, self.gate_id, 0, i)
					self.add_gate(new_neighbour, self.gate_id, new_neighbour.x - 1, i)
					self.gate_id += 1

			self.users = self.users | set([user])
			user.set_room(self)
			user.add_permission('room')

		self.notify_users()

	def add_gate(self, user, gate_id, x, y):
		if user not in self.gates.keys():
			self.gates[user] = []

		slot = Slot(x, y)
		slots = [g['slot'] for g in self.gates[user]]
		if slot not in slots:
			self.gates[user].append({'id': gate_id, 'slot': Slot(*slot)})

	def set_controller(self, user):
		self.controller = user

	def eat_food(self, link):
		maxi = max(instance['num'] for instance in self.snake)
		snake = next(instance['snake'] for instance in self.snake if instance['num'] == maxi)
		last = snake[-1].copy()
		self.__apply_move__(link)
		snake.append(last)
		self.pause /= 1.6
		self.rand_food()

	def rand_food(self):
		import random
		user = random.choice(tuple(self.users))
		slots = [u['snake'] for u in self.snake if u['user'] == user]
		import itertools
		slots = list(itertools.chain(*slots))

		food = Slot.rand_slot(user.x, user.y)
		while food in slots or food in self.gates[user]:
			food = Slot.rand_slot(user.x, user.y)
		self.food_user = [user]
		self.food = food

	def kill(self):
		self.alive = False
		for user in self.users:
			user.add_permission('can-exit')

	def find_other_user_by_gate(self, gate):
		use = (user for user in self.users if user is not self.controller)
		for user in use:
			for g in self.gates[user]:
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
		gate = next(gate for gate in self.gates[self.controller] if gate['slot'] == link)
		user1, slot1 = self.find_other_user_by_gate(gate)
		for instance in self.snake:
			if instance['num'] == 0:
				instance['snake'].pop(-1)
			instance['num'] += 1
		notify_variable(self.controller, 'controller', False, 'boolean')
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

		gates_slots = [g['slot'] for g in self.gates[self.controller]]
		if self.controller in self.food_user and link == self.food:
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
		if not self.moves:
			self.moves = [self.last_move]
		move = self.moves.pop(0)
		self.move_snake(move)
		self.last_move = move
		self.clear_empty()
		self.notify_users()

	def notify_users(self):
		length = sum(len(link['snake']) for link in self.snake)
		for user in self.users:
			snake = []
			for s in self.snake:
				if s['user'] is user:
					snake += s['snake']
			notify_variable(user, 'snake', str(snake), 'slots')
			notify_variable(user, 'alive', self.alive, 'boolean')
			notify_variable(user, 'link-count', length, 'number')
			notify_variable(user, 'gates', str([g['slot'] for g in self.gates[user]]), 'slots')
			notify_variable(user, 'food', str([self.food] if user in self.food_user else []), 'slots')
		for user in users:
			if user is not self.controller:
				user.add_permission('can-exit')
		notify_variable(self.controller, 'controller', True, 'boolean')
		self.controller.remove_permission('can-exit')

	def add_move(self, direction):
		if not self.moves or not (self.moves[-1] is direction or self.moves[-1] is NEG[direction]):
			self.moves.append(direction)

	def __str__(self):
		return 'Room {0}'.format(self.name)

	def __repr__(self):
		return str(self)

	def run(self):
		while self.alive:
			self.step()
			time.sleep(self.pause)
