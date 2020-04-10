"""
A PondBot implementation for Discord servers.
"""

import sys

import discord

import config
from bot import Bot, Message
from exceptions import BotShutdownException, BotRestartException


client = discord.Client()


class DiscordBot(Bot):
	"""
	A bot implementation for Discord servers.
	"""
	
	def run(self):
		"""
		Start the bot.
		"""
		
		DiscordBot._cur_bot = self
		self.set_up()
		
		config.load_config("discord")
		
		# The way discord.py suppresses errors means I need to get a bit janky
		# to maintain exception-based shutdown/restart differentiation.
		# client.stop_err is part of that.
		client.stop_err = None
		
		client.run(config.configs["discord"]["bot-token"])
		
		# Check if the client stopped because of a control-flow error.
		if client.stop_err:
			# If so, propogate that error to manage.py.
			raise client.stop_err


class DiscordMessage(Message):
	"""
	A message from a Discord user.
	"""
	
	def __init__(self, msg):
		super().__init__()
		self.raw_msg = msg
		self.text_content = msg.content
		self.sender_name = msg.author.display_name
		self.sender_id = msg.author.id
		
		for role in [r.id for r in self.raw_msg.author.roles]:
			perm_role_items = config.configs["discord"]["perm-roles"].items()
			for group, ranks in perm_role_items:
				# In case ranks weren't made as strings in the config file,
				# convert them to such.
				ranks = [str(r) for r in ranks]
				if role in ranks:
					self.sender_group = group
					break
		
		self._parse()
	
	async def reply(self):
		"""
		Reply to a received message.
		"""
		
		if self.reply_msg:
			await client.send_message(
				self.raw_msg.channel,
				self.reply_msg,
			)


bot = DiscordBot
		

@client.event
async def on_ready():
	"""
	Code to run once the bot has connected to the server.
	"""
	
	# Send a nice startup message upon joining a channel.
	if config.configs["discord"].get("startup-msg"):
		await client.send_message(
			discord.Object(config.configs["discord"]["default-channel"]),
			config.configs["discord"]["startup-msg"],
		),
		

@client.event
async def on_message(msg):
	"""
	Code to run when the bot receives a message.
	
	Args:
		msg: the received message.
	"""
	
	msg = DiscordMessage(msg)
	await msg.reply()


@client.event
async def on_error(*args, **kwargs):
	"""
	Code to run when the bot's run loop raises an error.
	"""
	
	# discord.py will normally suppress runtime errors from the bot, which
	# messes with shutdown/restart differentiation. Here we tell it to,
	# instead, if it's a bot restart/shutdown exception, log out gracefully.
	# Otherwise just propagate it out.
	
	err = sys.exc_info()
	# If it's a shutdown or restart error, log out and save the error for later
	# propagation.
	error_requires_graceful_stop = (
		issubclass(err[0], BotShutdownException)
		or issubclass(err[0], BotRestartException)
	)
	if error_requires_graceful_stop:
		
		# Send a parting message when the bot shuts down.
		if config.configs["discord"].get("shutdown-msg"):
			await client.send_message(
				discord.Object(config.configs["discord"]["default-channel"]),
				config.configs["discord"]["shutdown-msg"],
			)
		
		client.stop_err = err[0]
		await client.logout()
	
	# Otherwise, propogate the error.
	else:
		raise err[1]
