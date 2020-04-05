"""
Definitions for various useful exceptions.
"""


class CommandException(Exception):
	"""
	Generic expection for errors encountered when running commands.
	"""
	
	pass


class UnknownCommandException(CommandException):
	"""
	Exception for when a user attempts to use a nonexistant command.
	"""
	
	pass


class BotRestartException(Exception):
	"""
	Exception to be raised in order to signal the bot to restart.
	"""
	
	pass


class BotShutdownException(Exception):
	"""
	Exception to be raised in order to signal the bot to shut down.
	"""
	
	pass
