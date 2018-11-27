"""
Manage chat command interactions in the bot.
"""

import functools

import config
import cooldown
from exceptions import CommandException, UnknownCommandException
from handlers import messagehandler
from permissions import group_has_perm

dynamic_commands =  {} # command_name:command_func (str:callable)

# TODO More elegantly handle preventing stupid values/very long processes.
# TODO !quote list and pastebin the quotes json file.
# TODO !xquote with old list of nexusbot quotes: https://public.ds003.info/xenquotes/
# TODO Move command cooldowns to a config.

def register_commands():
	"""
	Load and register all dynamic commands for the bot.
	"""
	
	dynamic_commands.clear()
	
	for mod in config.configs["commands"]["registered-cmd-pls"]:
		# Just importing the modules will make the commands register themselves, because of @Command.
		register_com_mod(mod)

def register_com_mod(mod_name):
	"""
	Register a single command module.
	Args:
		mod_name -- name of the command module to register.
	"""
	
	__import__("plugins.command_plugins." + mod_name)


def delegate_command(cmd):
	"""
	Retrieve a callable command from its string name.
	
	Args:
		cmd -- the name of the command to retrieve.
		
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
		return (Command(static=True, cooldown=com_conf["statics-cooldown"], name=cmd, args_val=lambda: True)
				(lambda *args: com_conf["static-commands"][cmd]))
			
	raise UnknownCommandException("Unknown command: " + cmd)


def validate_command_args(cmd, args, alias=None):
	"""
	Validate the syntax of a set of arguments for the given command callable.
	
	Args:
		cmd ---- the callable command to validate arguments for.
		args --- the arguments to validate.
		alias -- the alias that the command was called with. Optional.
	"""
	
	cmd_name = alias or cmd.meta["name"]
	
	if not cmd.meta["args_val"](*args):
		raise CommandException("Invalid args. Usage: {prefix}{name} {usage}".format(
								prefix=config.configs["commands"]["command-prefix"],
								name=cmd_name, usage=cmd.meta["args_usage"]))


@messagehandler
def cmd_msg_handler(msg, _):
	com_conf = config.configs["commands"]
	
	if msg.text_content.startswith(com_conf["command-prefix"]):
		
		try: # Commands can throw errors, so those should be handled.
			# TODO Split up this section to make it less blocky.
			
			# Discard the command prefix and split the message into arguments along spaces.
			components = msg.text_content[len(com_conf["command-prefix"]):].split()
			cmd_name, args = components[0], components[1:]
			
			# Truncate arguments at 20 characters to avoid stupid values (e.g. !roll 9999999999...)
			args = [arg[:20] for arg in args]
			
			# Find and run the proper command function.
			command = delegate_command(cmd_name)
			name = "cmd." + command.meta["name"]
			
			# If commands are disabled or this particular command hasn't cooled down, stop resolution.
			# Either way, *never* disable the 'enable' command.
			if not (name == "cmd.enable" or (cooldown.has_cooled_down("cmds") and cooldown.has_cooled_down(name))):
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
			
			resp = command(*args)
			cooldown.set_cooldown(name, command.meta["cooldown"])
			if resp:
				return "{}: {}".format(msg.sender_name, resp)
		
		except CommandException as ex:
			# Only send an unknown command error if the config says to.
			if isinstance(ex, UnknownCommandException) and not config.configs["commands"]["err-unknown-cmd"]:
				return
			
			# If a command threw an error, tell that to the user.
			return "{user}: Error - {errmsg}".format(
						user=msg.sender_name, errmsg=ex.args[0])


class Command:
	"""
	Used as a decorator to define command objects.
	
	Attributes:
		meta -- a dictionary of parameters passed on object initialisation.
	
	A static command is one which always replies with the same value, regardless of arguments or other context.
	Static and dynamic commands are disjoint and all-encompassing.
	"""
	
	def __init__(self, **kwargs):
		"""
		Specify certain meta command properties.
		
		Valid kwargs:
			static -------- whether this command takes any arguments.
			cooldown ------ minimum number of seconds between uses of this command, to avoid spamming.
			args_val ------ a callable that returns True if the command arguments are well-formed, or False otherwise.
			args_usage ---- a string showing the proper syntax for the command arguments.
			name ---------- the name that this command is called by; by default, the name of the wrapped function.
			no_perms_msg -- an optional message to return if someone uses this command without the proper permissions.
		"""
		
		# Provide some defaults for kwargs.
		self.meta = {
			"static": False,
			"cooldown": 5,
			"args_val": lambda *args: True,
			"args_usage": "<arguments>",
			"name": None,
			"no_perms_msg": None,
		}
		self.meta.update(kwargs)
	
	def __call__(self, cmd):
		"""
		Wrap the given command and save it to the command list, if it's dynamic.
		
		Args:
			cmd -- the command to be wrapped.

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
			# Save it as the given name or, failing that, the name of the function.
			dynamic_commands[self.meta["name"]] = wrapped_func
		
		return wrapped_func


register_commands()
