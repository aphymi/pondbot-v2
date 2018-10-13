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
		DiscordBot._cur_bot = self
		self.set_up()
		config.load_config("discord")
		if "commands" in config.configs["general"]["plugins"]:
			from plugins.commands import register_com_mod
			register_com_mod("discord")
		
		# The way discord.py suppresses errors means I need to get a bit janky to maintain exception-based
		# 	shutdown/restart differentiation. client.stop_err is part of that.
		client.stop_err = None
		
		client.run(config.configs["discord"]["bot-token"])
		
		# Check if the client stopped because of a control-flow error.
		if client.stop_err:
			raise client.stop_err # If so, propogate that error to manage.py.


class DiscordMessage(Message):
	"""
	A message from a Discord user.
	"""
	
	def __init__(self, msg):
		self.raw_msg = msg
		self.text_content = msg.content
		self.sender_name = msg.author.name
		self.sender_id = msg.auth.id
		
		for role in [r.id for r in msg.author.roles]:
			for group, ranks in config.configs["discord"]["perm-groups"]:
				if role in ranks:
					msg.sender_group = group
					break
		
		self._parse()
	
	async def reply(self):
		if self.reply_msg:
			await client.send_message(self.raw_msg.channel, self.reply_msg)

bot = DiscordBot
		

@client.event
async def on_ready():
	await client.send_message(discord.Object(config.configs["discord"]["startup-channel"]),
							  config.configs["discord"]["startup-msg"])

@client.event
async def on_message(msg):
	msg = DiscordMessage(msg)
	await msg.reply()

@client.event
async def on_error(event, *args, **kwargs):
	# discord.py will normally suppress runtime errors from the bot, which would fuck with
	# 	shutdown/restart differentiation. Instead, if it's a bot restart/shutdown exception,
	# 	log out gracefully. Otherwise just propogate it out.
	
	err = sys.exc_info()
	# If it's a shutdown or restart error, log out and save the error for later propgation.
	if issubclass(err[0], BotShutdownException) or issubclass(err[0], BotRestartException):
		client.stop_err = err[0]
		await client.logout()
	
	# Otherwise, propogate the error.
	else:
		raise err[1]
