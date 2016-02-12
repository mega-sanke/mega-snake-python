import  exceptions
import select
import socket

import commander
import globals

__unconfirmed__ = []  # type: list[socket.socket]

__notifies__ = []  # type: list[dict]

server_socket = socket.socket()

server_socket.bind(('0.0.0.0', 8820))

server_socket.listen(3)


def split(*sockets):
	global server_socket
	if len(sockets) == 0:
		return None, [], []
	serverr = [s for s in sockets if s is server_socket]
	server = None if len(serverr) else next(serverr)
	unconfirmed = [sock for sock in sockets if sock in __unconfirmed__]
	users = [user for user in globals.users if user.socket in sockets]

	return server, unconfirmed, users

try:
	while True:
		sockets = [server_socket] + [user.socket for user in globals.users]
		rlist, wlist, xlist = select.select(sockets, sockets, sockets)  # type: tuple(list[socket.socket])

		r_server_socket, r_unconfirmed, r_users = split(*rlist)
		w_server_socket, w_unconfirmed, w_users = split(*wlist)
		x_server_socket, x_unconfirmed, x_users = split(*xlist)

		if r_server_socket is not None:
			print "New User!!!"
			sock, _ = r_server_socket.accept()  # type: socket.socket
			__unconfirmed__.append(sock)

		for sock in __unconfirmed__:
			m = sock.recv(1024)  # type: str
			m = m.split(',')  # type: list[str]
			m.insert(0, 'connect')
			print "confirmed by: ", m
			commander.execute_command(sock, *m)

		for user in r_users:
			m = user.socket.recv(1024)  # type: str
			m = m.split(',')   # type: list[str]
			print m
			commander.execute_command(user, *m)
except exceptions.IOError:
	for s in __unconfirmed__:
		s.close()

	for u in globals.users:
		u.socket.close()




