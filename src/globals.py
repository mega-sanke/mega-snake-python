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
        return str(self.coordinates)

    def __repr__(self):
        return repr(self.coordinates)

    def __len__(self):
        return len(self.coordinates)

    def __eq__(self, other):
        return (self.coordinates == other.coordinates) == ([True] * len(self))

    def copy(self):
        return Slot(*self.coordinates)


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
        self.x_ = gridx
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


class Room:
    def __init__(self, name, admin, password=None):
        self.name = name
        self.admin = admin
        self.password = password
        self.users = set([])
        self.food_user = admin
        self.controller = admin
        self.alive = True
        self.snake = [{'user': self.controller, 'num': 0, 'snake': []}]

    def parse_str(self, room):
        global rooms
        return next(r for r in rooms if r.name == room)

    def add_user(self, *new_users):
        self.users = self.users | set(new_users)
        for user in new_users:
            user.set_room(self)
            user.add_permission('room')

    def set_controller(self, user):
        self.controller = user

    def eat_food(self, link):
        self.__apply_move__(link)
        maxi = max(instance['num'] for instance in self.snake)
        snake = next(instance['snake'] for instance in self.snake if instance['num'] == maxi)
        snake.append(snake[-1])

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
        first_part['snake'].insart(0, link)
        if not len(snake['snake']):
            self.snake.remove(snake)

    def __apply_gate__(self, link):
        gate = next(gate for gate in self.controller.gates if gate['slot'] == link)
        user1, slot1 = self.find_other_user_by_gate(gate)
        for instance in self.snake:
            instance['num'] += 1
        self.set_controller(user1)
        self.snake.append({'user': user1, 'num': 0, 'snake': [slot1]})

    def get_snake(self, user):
        chains = list(a['snake'] for a in self.snake if a['user'] == user)
        import itertools
        return set(itertools.chain(*chains))

    def move_snake(self, direction):
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

        if self.controller is self.food_user and link == self.food:
            self.eat_food(link)
        elif link in gates_slots:
            self.__apply_gate__(link)
        elif link[0] < 0 or link[0] >= self.controller.x or link[1] < 0 or link[1] >= self.controller.y or (
                    link in {b for b in next(a['snake'] for a in self.snake if a['num'] == 0)}):
            self.kill()
        else:
            self.__apply_move__(link)

    def __str__(self):
        return 'Room {0}'.format(self.name)

    def __repr__(self):
        return str(self)
