"""
Manage chat command interactions in the bot.
"""

import functools

import yaml

from config_handler import configs

from exceptions import CommandException

dynamic_commands =  {} # command_name:command_func (str:callable)

# Command modules to take commands from.
registered_modules = [
	"misc",
]


def register_commands():
	"""
	Load and register all commands for the bot.
	Should only be called once per run.
	"""
	
	dynamic_commands.clear()
	
	# TODO See if importing command mods gets fucked up after a bot restart
	for mod in registered_modules:
		# Just importing the modules will make the commands register themselves, because of @Command.
		__import__("command_mods." + mod)


def delegate_command(cmd):
	"""
	Retrieve a callable command from its string name.
	
	Args:
		cmd: the name of the command to retrieve
		
	Returns: the callable for the desired command

	"""
	
	com_conf = configs["commands"]
	
	# Check if the command is an alias for another command.
	for com in com_conf["aliases"]:
		if cmd in com_conf["aliases"][com]:
			cmd = com
	
	if cmd in dynamic_commands:
		return dynamic_commands[cmd]
	elif cmd in com_conf["static-commands"]:
		return (Command(static=True, cooldown=com_conf["statics-cooldown"], name=cmd)
				(lambda args: com_conf["static-commands"][cmd]))
			
	raise CommandException("Unknown command")


def validate_command_args(cmd, args):
	"""
	Validate the syntax of a set of arguments for the given command callable.
	
	Args:
		cmd:  The callable command to validate arguments for.
		args: The arguments to validate.
	"""
	
	if not (cmd.meta["args_val"](args)):
		# TODO Make it return the alias the command was called with in the invalid args message
		raise CommandException("Invalid args. Usage: !%s %s" % (cmd.meta["name"], cmd.meta["args_usage"]))
	# TODO Check if calling user has permission to run this command.
	pass


class Command:
	"""
	Used as a decorator to define command objects.
	
	Attributes:
		static (bool) ------ If True, this command is static. If False, it is dynamic.
		
		cooldown (number) -- The mimimum time (in seconds) between when a command was last used,
				and when it can be used again.
				
		args_val (func) ---- A function to be run and given the list of command arguments as a parameter.
				When the arguments are syntactically valid for the command, it returns True. False otherwise.
				
		args_usage (str) --- A string describing the syntactic form of arguments to this command.
	
	A static command is one which always replies with the same value, regardless of arguments or other context.
	Static and dynamic commands are disjoint and all-encompassing.
	"""
	
	def __init__(self, **kwargs): # TODO 'name' kwarg is only really used for static commands. Is there a better solution?
		"""
		Specify certain meta command properties.
		
		Valid kwargs:
			static -------- whether this command takes any arguments.
			cooldown ------ minimum number of seconds between uses of this command, to avoid spamming.
			args_val ------ a callable that returns True if the command arguments are well-formed, or False otherwise.
			args_usage ---- a string showing the proper syntax for the command arguments.
			name ---------- the name that this command is called by; by default, the name of the wrapped function.
			no_perms_msg -- an optional specific message to return if someone uses this command without permission
		"""
		
		self.meta = kwargs
	
	def __call__(self, cmd): # TODO Write a better one-line descr
		"""
		Wrap the given command with a few extra bits.
		
		Args:
			cmd: The command to be wrapped.

		Returns: The wrapped function
		"""
		
		@functools.wraps(cmd)
		def wrapped_func(args=()):
			if self.meta.get("static"):
				# Don't bother passing any received arguments.
				args.clear()
			
			return cmd(*args)
		
		wrapped_func.meta = self.meta
		
		# Don't save static commands to the list
		if not self.meta.get("static"):
			# Save it as the given name or, failing that, the name of the function.
			dynamic_commands[self.meta.get("name") or cmd.__name__] = wrapped_func
		
		return wrapped_func



