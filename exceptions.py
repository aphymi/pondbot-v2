"""
Definitions for various useful exceptions.
"""


class CommandException(Exception):
	"""
	Exception to be raised when there is some user error when attempting to use a command.
	"""
	
	pass

class UnknownCommandException(CommandException):
	"""
	Exception to be raised when a user attempts to use a nonexistant command.
	"""
	
	pass


class BotRestartException(Exception):
	"""
	Exception to be raised in order to restart the bot.
	"""
	
	pass


class BotShutdownException(Exception):
	"""
	Exception to be raised in order to make the bot shut down.
	"""
	
	pass
