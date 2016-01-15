import socket
from select import select
from xml_parser import *
from protocol import *

keys = get_fields('fields.xml')
last_id = 0
gate_last_id = 0
walls = {'north': 'NORTH', 'west': 'WEST', 'east': 'EAST', 'south': 'SOUTH'}
walls_neg = {'north': 'SOUTH', 'west': 'EAST', 'east': 'WEST', 'south': 'NORTH'}

players = []
temp_players = []

def add_player(socket):
    global last_id
    global temp_players
    player = {'socket': socket, 'id': last_id, 'walls': {}}
    m = {
        keys['TARGET']: 'BROADCAST',
        keys['TYPE']: 'DATA',
        keys['ID']: last_id
    }
    if not len(players):
        m[keys['START']] = 'emptyField'

    send(players, m)
    temp_players.append(player)
    last_id += 1


'''
this function return a random player that has free wall, and a random free wall
'''
def get_player_no_wall():
    global walls
    global players
    import random

    free = [p for p in players if len(p['walls']) < 4]
    player = random.choice(free)
    wall = random.choice(walls.keys())
    while wall in player['walls'].keys():
        wall = random.choice(wall.keys())
    player['walls'][wall] = walls[wall]
    return player, wall


def broadcast(msg, *no):
    for p in players:
        if p not in no:
            send(p, msg)


def send(player, msg):
    player['socket'].send(encode(msg))


def recv(msg, player):
    global players

    msg = decode(msg)
    if keys['NEIGHBOR_ADD_COUNT'] in msg:
        width_count = msg[keys['WIDTH']]
        height_count = msg[keys['HEIGHT']]
        p, wall = get_player_no_wall()
        player['walls'][wall] = walls[wall]



    if keys['GATE_ID'] in msg:
        pass
    if keys['NEIGHBOR_ADD'] in msg:
        pass
    if keys['NEIGHBOR_ADD_SIZE'] in msg:
        pass
    if keys['OK'] in msg:
        pass
    if keys['TARGET'] in msg:
        pass
    if keys['FOOD'] in msg:
        pass
    if keys['NEIGHBOR_ADD_WIND'] in msg:
        pass
    if keys['DEAD'] in msg:
        pass
    if keys['FIRST_CONNECT'] in msg:
        pass
    if keys['START'] in msg:
        pass
    if keys['GATE_PLYER_ID'] in msg:
        pass
    if keys['GATE_PREV_MOVE'] in msg:
        pass
    if keys['GATE'] in msg:
        pass
    if keys['TYPE'] in msg:
        pass
    if keys['ID'] in msg:
        pass



def __find_player_by_socket__(socket):
    return [player for player in players if player['socket'] == socket][0]


if __name__ == '__name__':
    pass
