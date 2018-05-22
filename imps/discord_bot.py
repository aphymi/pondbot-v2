"""
A PondBot implementation for Discord servers.
"""

import discord
import sys

from bot import Bot, Message
from commands import register_com_mod
import config_handler
from exceptions import BotShutdownException, BotRestartException

client = discord.Client()

class DiscordBot(Bot):
	"""
	A bot implementation for Discord servers.
	"""
	
	def run(self):
		self.set_up()
		config_handler.load_config("discord")
		register_com_mod("discord")
		
		# The way discord.py suppresses errors means I need to get a bit janky to maintain exception-based
		# 	shutdown/restart differentiation. client.stop_err is part of that.
		client.stop_err = None
		
		client.run(config_handler.configs["discord"]["bot-token"])
		
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
		self.reply_msg = None
		
		self._parse()
	
	async def reply(self):
		if self.reply_msg:
			await client.send_message(self.raw_msg.channel, self.reply_msg)

bot = DiscordBot
		

@client.event
async def on_ready():
	await client.send_message(discord.Object(config_handler.configs["discord"]["startup-channel"]),
							  config_handler.configs["discord"]["startup-msg"])

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
	
	# Otherwise, propogate the error immediately.
	else:
		raise err[1]
