import  exceptions
import select
import socket

import commander
import globals

__unconfirmed__ = []  # type: list[socket.socket]

__unsigned__ = []  # type: list[socket.socket]

__notifies__ = []  # type: list[dict]

server_socket = socket.socket()

server_socket.bind(('0.0.0.0', 8820))

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
	unconfirmed = [sock for sock in sockets if sock in __unconfirmed__]   # type: list[socket.socket]
	unsigned = [sock for sock in sockets if sock in __unsigned__]   # type: list[socket.socket]
	users = [user for user in globals.users if user.socket in sockets]   # type: socket.socket

	return server, unconfirmed, unsigned, users


# try:
print commander.__commands__
while True:
	sockets = [server_socket] + __unconfirmed__ + __unsigned__ + [user.socket for user in globals.users]
	rlist, wlist, xlist = select.select(sockets, sockets, sockets)  # type: tuple(list[socket.socket]
	r_server_socket, r_unconfirmed, r_unsigned, r_users = split(*rlist)
	w_server_socket, w_unconfirmed, w_unsigned, w_users = split(*wlist)
	x_server_socket, x_unconfirmed, x_unsigned, x_users = split(*xlist)

	if r_server_socket is not None:
		print "New User!!!"
		sock, _ = r_server_socket.accept()  # type: socket.socket
		__unconfirmed__.append(sock)

	for sock in r_unconfirmed:
		m = sock.recv(1024)  # type: str
		__unconfirmed__.remove(sock)
		__unsigned__.append(sock)
		print "confirmed by: ", m

	for sock in r_unsigned:
		m = sock.recv(1024)  # type: str
		m = m.split(',')  # type: list[str]
		__unsigned__.remove(sock)
		m.insert(0, 'connect')
		print "signed by: ", m
		commander.execute_command(sock, *m)
		print globals.users

	for user in r_users:
		m = user.socket.recv(1024)  # type: str
		m = m.split(',')  # type: list[str]
		print m
		commander.execute_command(user, *m)


# except exceptions.IOError:
# 	for s in __unconfirmed__:
# 		s.close()
#
# 	for u in globals.users:
# 		u.socket.close()
