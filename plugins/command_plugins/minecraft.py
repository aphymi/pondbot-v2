"""
Commands which are generally useful for a Minecraft server.
"""

import requests

from plugins.commands import Command
import collections


@Command(args_val=(lambda *args: args), args_usage="<name>")
def welcome(*name):
	"""
	Welcome a new member of the server.
	"""
	
	# Join the name in case it contains a space.
	return "Everyone please welcome {} to the server!".format(" ".join(name))


@Command(
	args_val=(lambda *args: len(args) == 1 and args[0].isdigit()),
	args_usage="<# of items>",
)
def stacks(items):
	"""
	Find the number of stacks an item breaks down into.
	"""
	
	items = int(items)
	stacks, left = items // 64, items % 64
	
	# "x items break down into y stacks with z items left over."
	return (
		f"{items} item{'' if items == 1 else 's'} "
		f"break{'s' if items == 1 else ''} down into "
		f"{stacks} stack{'' if stacks == 1 else 's'} "
		f"with {left} item{'' if left == 1 else 's'} left over."
	)


@Command(
	args_val=(lambda *args: len(args) == 1 and args[0].isdigit()),
	args_usage="<# of stacks>",
)
def items(stacks):
	"""
	Find the number of items in a number of stacks.
	"""
	
	stacks = int(stacks)
	items = stacks * 64
	
	return (
		f"{stacks} stack{'' if stacks == 1 else 's'} break down into "
		f"{items} item{'' if items == 1 else 's'}."
	)


@Command(args_val=(lambda *args: not args), args_usage="")
def mcstatus():
	"""
	Check the status of Mojang's servers.
	"""
	
	server_statuses = requests.get("http://status.mojang.com/check").json()
	
	# Mojang's status API has a weird format. Instead of a single multi-key
	# dict, it's an array of single-key dictionaries.
	down_servers = [
		server
		for server, status in collections.ChainMap(*server_statuses).items()
		if status != "green"
	]
	
	if down_servers:
		return "Possibly down: {}".format(", ".join(down_servers))
	
	else:
		return "All Mojang servers are up."
