
import select
import socket

import commander
import globals

print socket.gethostbyname(socket.gethostname())

__unsigned__ = []  # type: list[socket.socket]

__notifies__ = []  # type: list[dict]

admin = globals.User('admin', None, 0,0)
admin.add_permission('super-admin')

server_socket = socket.socket()

server_socket.bind(('0.0.0.0', 1234))

server_socket.listen(3)


def split(*sockets):

	"""
	This function split socket to the categories: server_socket (only single socket), unconfirmd,
	unsinged and users (return the user objects)

	:param sockets: the socket to split
	:type sockets: socket.socket
	:return: a tuple of the categorized sockets
	:rtype: tuple[list]
	"""
	global server_socket

	serverr = [s for s in sockets if s is server_socket]
	server = None if not len(serverr) else next(iter(serverr))  # type: list[socket.socket
	unsigned = [sock for sock in sockets if sock in __unsigned__]   # type: list[socket.socket]
	users = [user for user in globals.users if user.socket in sockets]   # type: socket.socket

	return server, unsigned, users


def admin_user():
	while True:
		m = raw_input()
		m = m.split(' ')  # type: list[str]

		commander.execute_command(admin, *m)

import thread
thread.start_new_thread ( admin_user ,())


while True:
	sockets = [server_socket]  + __unsigned__ + [user.socket for user in globals.users]
	rlist, wlist, xlist = select.select(sockets, sockets, sockets)  # type: tuple(list[socket.socket]
	r_server_socket, r_unsigned, r_users = split(*rlist)
	w_server_socket, w_unsigned, w_users = split(*wlist)
	x_server_socket, x_unsigned, x_users = split(*xlist)

	if r_server_socket is not None:
		sock, _ = r_server_socket.accept()  # type: socket.socket
		__unsigned__.append(sock)

	for sock in r_unsigned:

		m = sock.recv(1024)  # type: str
		m = m.split(',')  # type: list[str]
		__unsigned__.remove(sock)
		m.insert(0, 'connect')
		commander.execute_command(sock, *m)
		if len(globals.users) == 1:
			commander.execute_command(globals.users[0], 'create-room', 'test', '1234')

	for user in r_users:
		m = user.socket.recv(1024)  # type: str
		m = m[0:-1] # removing the '\n' in the end
		m = m.split(',')  # type: list[str]
		commander.execute_command(user, *m)