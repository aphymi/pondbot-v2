"""
A PondBot implementation for Discord servers.
"""

import discord

from bot import Bot, Message
import config_handler
from exceptions import BotShutdownException

client = discord.Client()

class DiscordBot(Bot):
	"""
	A bot implementation for Discord servers.
	"""
	
	def run(self):
		self.set_up()
		config_handler.load_config("discord")
		
		client.run(config_handler.configs["discord"]["bot-token"])


class DiscordMessage(Message):
	"""
	A message from a Discord user.
	"""
	
	def __init__(self, msg):
		self.raw_msg = msg
		self.text_content = msg.content
		self.sender_name = msg.author.name
		self.reply_msg = None
		
		# TODO Move this somewhere less fucky
		if self.text_content == "!quit":
			client.logout()
			raise BotShutdownException
		
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
