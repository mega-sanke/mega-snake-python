import globals


def __notify__(user, type, *message):

		"""
		This function send a notifications for the user

		:param user: the user whom this function notify
		:type user: globals.User
		:param type: the type of the message
		:type type: str
		:param message: the contact for the message
		:type message: list[str]
		"""

		message = list(message)
		for (i, v) in enumerate(message):
			message[i] = str(v)
		message.insert(0, type)
		message = '&&'.join(message)
		user.socket.sendall(message + '\n')


def notify_error(user, msg):
	__notify__(user, 'ERROR', msg)


def notify_message(user, msg):
	__notify__(user, 'MESSAGE', msg)


def notify_variable(user, name, value):
	__notify__(user, 'VALUE', name, value)