rooms = []
users = []

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

    def add_gate(self, id, x, y = None):
        slot = (x,y)
        if y is None:
            slot = x

        slots = {g.slot for g in self.gates}
        if slot not in slots:
            self.gates = self.gates | {Gate(id, slot)}



    def add_permission(self, *pers):
        self.permissions = self.permissions | set(pers)

    def remove_permissions(self, *per):
        self.permissions = self.permissions - set(per)


class Room:
    def __init__(self, name, number ,admin, password=None):
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





class Gate:
    def __init__(self, id, x, y=None):
        self.id = id
        self.slot = (x, y) if y is not None else x

    def __eq__(self, other):
        return self.id == other.id and self.slot == other.slot






