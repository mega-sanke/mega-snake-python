rooms = []
users = []


class User:
    def __init__(self, name, socket, gridx, gridy):
        self.name = name
        self.socket = socket
        self.permissions = []
        self.x = gridx
        self.y = gridy
        self.gates = {}
        self.room = None


    def set_room(self, room):
        room.add_user(self)
        self.room = room

    def clear_room(self):
        self.set_room(None)

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

    def move_snake(self, dir):
        link = self.snake[0].copy()
        self.snake.pop(-1)
        if dir == 'N':
            link[0] -=

