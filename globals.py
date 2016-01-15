rooms = []
users = []


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


class User:
    def __init__(self, name, socket, gridx, gridy):
        self.name = name
        self.socket = socket
        self.permissions = []
        self.x_ = gridx
        self.y = gridy
        self.gates = {}
        self.room = None

    def set_room(self, room):
        room.add_user(self)
        self.room = room

    def clear_room(self):
        self.set_room(None)

    def add_gate(self, id, x, y=None):
        slot = Slot(x, y)
        if y is None:
            slot = x

        slots = {g['slot'] for g in self.gates}
        if slot not in slots:
            self.gates = self.gates | {{'id': id, 'slot': Slot(*slot)}}

    def add_permission(self, *pers):
        self.permissions = self.permissions | set(pers)

    def remove_permissions(self, *per):
        self.permissions = self.permissions - set(per)


class Room:
    def __init__(self, name, number, admin, password=None):
        self.name = name
        self.number = number
        self.admin = admin
        self.password = password
        self.users = {}
        self.food_user = admin
        self.controller = admin
        self.snake = []

    def add_user(self, *new_users):
        self.users = self.users | set(new_users)
        for user in new_users:
            user.set_room(self)
            user.add_permission('room')

    def set_controller(self, user):
        self.controller = user

    def eat_food(self):
        pass

    def move_snake(self, direction):
        link = self.snake[0].copy()
        self.snake.pop(-1)
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
            self.eat_food()
        elif link in gates_slots:
            gate = next(gate for gate in self.controller.gates if gate['solot'] ==  link)
            room
        elif link[0] < 0 or link[0] >= self.controller.x or link[1] < 0 or link[1] >= self.controller.y:
            pass











