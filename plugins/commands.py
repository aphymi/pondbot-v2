"""
Manage chat command interactions in the bot.
"""

import functools

import config
import cooldown
from exceptions import CommandException, UnknownCommandException
from handlers import MessageHandler
from permissions import group_has_perm

dynamic_commands = {}


def register_commands():
	"""
	Load and register all dynamic commands for the bot.
	"""
	
	dynamic_commands.clear()
	
	for mod in config.configs["commands"]["registered-cmd-pls"]:
		# Simple importing the modules will make the commands register
		# themselves, as a side-effect of @Command.
		register_com_mod(mod)


def register_com_mod(mod_name):
	"""
	Register a single command module.
	
	Args:
		mod_name: name of the command module to register.
	"""
	
	__import__(f"plugins.command_plugins.{mod_name}")


def delegate_command(cmd):
	"""
	Retrieve a callable command from its string name.
	
	Args:
		cmd: the name of the command to retrieve.
		
	Returns: the callable for the desired command.

	"""
	
	com_conf = config.configs["commands"]
	
	# Check if the command is an alias for another command.
	for com in com_conf["aliases"]:
		if cmd in com_conf["aliases"][com]:
			cmd = com
	
	if cmd in dynamic_commands:
		return dynamic_commands[cmd]
		
	elif cmd in com_conf["static-commands"]:
		StaticCommand = Command(
			static=True,
			cooldown=com_conf["statics-cooldown"],
			name=cmd,
			args_val=lambda: True,
		)
		return StaticCommand(
			lambda *args: com_conf["static-commands"][cmd],
		)
			
	raise UnknownCommandException("Unknown command: " + cmd)


def validate_command_args(cmd, args, alias=None):
	"""
	Validate the syntax of a set of arguments for the given command callable.
	
	Args:
		cmd: the callable command to validate arguments for.
		args: the arguments to validate.
		alias: the alias that the command was called with. Optional.
	"""
	
	cmd_name = alias or cmd.meta["name"]
	
	if not cmd.meta["args_val"](*args):
		prefix = config.configs["commands"]["command-prefix"]
		usage = cmd.meta["args_usage"]
		
		raise CommandException(
			f"Invalid args. Usage: {prefix}{cmd_name} {usage}",
		)


@MessageHandler
def cmd_msg_handler(msg):
	"""
	Message event handler for commands.
	"""
	
	com_conf = config.configs["commands"]
	
	if msg.text_content.startswith(com_conf["command-prefix"]):
		
		try:
			# Commands can throw errors, so those should be handled.
			
			# Discard the command prefix and split the message into arguments
			# along spaces.
			components = (
				msg.text_content[len(com_conf["command-prefix"]):]
				.split()
			)
			cmd_name, args = components[0], components[1:]
			
			# Truncate arguments at 20 characters to avoid stupid values
			# e.g. !roll 9999999999...
			args = [arg[:20] for arg in args]
			
			# Find and run the proper command function.
			command = delegate_command(cmd_name)
			name = "cmd." + command.meta["name"]
			
			# If commands are disabled or this particular command hasn't cooled
			# down, stop resolution. Either way, never disable the 'enable'
			# command.
			disableable = (
				name == "cmd.enable"
				or (
					cooldown.has_cooled_down("cmds")
					and cooldown.has_cooled_down(name)
				)
			)
			if not disableable:
				return
			
			if command.meta["static"]:
				perm = "cmd.statics"
			else:
				perm = name
			
			# Check that the user has perms.
			if not group_has_perm(msg.sender_group, perm):
				if command.meta["no_perms_msg"]:
					raise CommandException(command.meta["no_perms_msg"])
				raise CommandException("Insufficient permissions.")
			
			validate_command_args(command, args, cmd_name)
			
			if command.meta["pass_msg"]:
				args = [msg] + args
				
			resp = command(*args)
			cooldown.set_cooldown(name, command.meta["cooldown"])
			if resp:
				# XOR
				prepend_name = (
					com_conf["prepend_name"]
					!= (command.meta["name"] in com_conf["prepend-exceptions"])
				)
				if prepend_name:
					resp = f"{msg.sender_name}: {resp}"
					
				return resp
		
		except CommandException as ex:
			# Avoid sending an error if the exception is due to an unknown
			# command, and those are configured to be silent.
			silence_error = (
				isinstance(ex, UnknownCommandException)
				and not config.configs["commands"]["err-unknown-cmd"]
			)
			
			if not silence_error:
				return f"{msg.sender_name}: Error - {ex.args[0]}"


class Command:
	"""
	Used as a decorator to define command objects.
	
	Attributes:
		meta: a dictionary of parameters passed on object initialisation.
	
	A static command is one which always replies with the same value,
	regardless of arguments or other context. Static and dynamic commands are
	disjoint and all-encompassing.
	"""
	
	def __init__(self, **kwargs):
		"""
		Specify certain meta command properties.
		
		Valid kwargs:
			static: whether this command takes any arguments.
			cooldown: minimum number of seconds between uses of this command,
				to avoid spamming.
			args_val: a callable that returns True if the command arguments are
				well-formed, or False otherwise.
			args_usage: a string showing the proper syntax for the command
				arguments.
			name: the name that this command is called by; by default, the name
				of the wrapped function.
			no_perms_msg: an optional message to return if someone uses this
				command without the proper permissions.
			pass_msg: whether to pass the Message object that triggered this
				command to the command function.
		"""
		
		# Provide some defaults for kwargs.
		self.meta = {
			"static": False,
			"cooldown": 5,
			"args_val": lambda *args: True,
			"args_usage": "<arguments>",
			"name": None,
			"no_perms_msg": None,
			"pass_msg": False
		}
		self.meta.update(kwargs)
	
	def __call__(self, cmd):
		"""
		Wrap the given command and save it to the command list, if it's dynamic.
		
		Args:
			cmd: the command to be wrapped.

		Returns: The wrapped function.
		"""
		
		@functools.wraps(cmd)
		def wrapped_func(*args):
			if self.meta["static"]:
				# Don't bother passing any received arguments.
				return cmd()
			
			return cmd(*args)
		
		wrapped_func.meta = self.meta
		
		# Don't save static commands to the list
		if not self.meta["static"]:
			if not self.meta["name"]:
				self.meta["name"] = cmd.__name__
			# Save it as the given name or, failing that, the name of the
			# function.
			dynamic_commands[self.meta["name"]] = wrapped_func
		
		return wrapped_func


register_commands()
