"""
Commands that affect the bot's functionality.

Commands:
	disable [cmd...]
	enable [cmd...]
	reload [conf...]
	shutdown
	restart
"""
# TODO Unify command module docstrings.
# TODO Change command modules to command plugins, in plugins.commands_plugins

import config
from cooldown import set_cooldown, has_cooled_down, remove_cooldown, _cooldowns as cooldown_list
from exceptions import BotRestartException, BotShutdownException
from plugins.commands import Command, CommandException, delegate_command


@Command(args_usage="[cmd...]")
def disable(*cmds):
	"""
	Disable some or all commands.

	Args:
		*cmds -- Command names

	If no arguments are given, all commands will be disabled.
	"""
	
	# No commands were given, so disable them all.
	if not cmds:
		set_cooldown("cmds", forever=True)
		return "All commands disabled."
	
	# Disable individual commands. They might be given by alias, so need to resolve those.
	cmd_names = []
	for cmd in cmds:
		name = delegate_command(cmd).meta["name"]
		if name == "enable":
			raise CommandException("Cannot disable the enable command.")
		
		cmd_names.append(name)
	
	for name in cmd_names:
		set_cooldown("cmd." + name, forever=True)
		return "Command%s re-enabled." % ("s" if len(cmd_names) > 1 else "")


@Command(args_usage="[cmd...]")
def enable(*cmds):
	"""
	Re-enable some or all disabled commands.

	Args:
		*cmds -- Command names

	If no arguments are given, all disabled commands will be re-enabled.
	Has the side effect/feature of immediately finishing the cooldown of included cmds.
	"""
	
	# Don't need to check whether c is cooled down, because removing it won't have any affect anything even if it is.
	disabled_cmds = filter(lambda c: c.startswith("cmd."),
						   cooldown_list.keys())  # Accessing private vars is sketchy, but it's useful here.
	
	if not cmds:
		if has_cooled_down("cmds") and not disabled_cmds:
			raise CommandException("No disabled commands.")
		
		for cmd in ["cmds"] + list(disabled_cmds):
			remove_cooldown(cmd)
		
		return "All commands re-enabled."
	
	cmd_names = []
	for cmd in cmds:
		name = delegate_command(cmd).meta["name"]
		cmd_names.append(name)
		
		if has_cooled_down("cmd." + name):
			raise CommandException("Command isn't disabled: %s" % cmd)
	
	# Remove duplicates.
	cmd_names = list(set(cmd_names))
	for name in cmd_names:
		remove_cooldown(name)
	
	return "Command%s re-enabled." % ("s" if len(cmd_names) > 1 else "")


@Command(args_usage="[conf...]")
def reload(*configs):
	"""
	Reload specific config files, or all of them at once.
	
	Args:
		*configs -- list of configs to reload.

	If *configs is omitted, all config files will be reloaded.
	"""
	
	for conf in configs:
		if conf not in config.configs:
			raise CommandException("Unknown config: " + conf)
	
	if not configs:
		configs = config.configs.keys()
	
	for conf in configs:
		config.load_config(conf)
		
	return "Config%s reloaded." % ("s" if len(configs) > 1 else "")


@Command(args_val=(lambda *args: not args), args_usage="")
def shutdown():
	"""
	Shut down the bot.
	"""
	
	raise BotShutdownException

@Command(args_val=(lambda *args: not args), args_usage="")
def restart():
	"""
	Restart the bot.
	"""
	
	raise BotRestartException
