import errno
import logging
import os
import shutil

import yaml

import config_handler
import commands

# TODO 'Expansions' module? Use to get title and such from YT links.

class Bot:
	"""
	Abstract class for the chat bot.
	"""
	
	def run(self):
		"""
		Perform whatever work is needed in order to start and run the bot.
		"""
		
		raise NotImplementedError("run() has not been implemented")


class Message:
	"""
	Abstract class for working with messages.
	"""
	
	def __init__(self):
		self.raw_msg = None
		self.reply_msg = None
		self.text_content = None
		self.sender_name = None
	
	def _parse(self):
		"""
		Parse and do whatever work necessary for the message.
			If the message necessitates a reply, save it to self.reply_msg.
		"""
		
		com_conf = config_handler.configs["commands"]
		
		# Check if the message is a command.
		if self.text_content.startswith(com_conf["command-prefix"]):
			try:
				components = self.text_content[len(com_conf["command-prefix"]):].split()
				cmd_name, args = components[0], components[1:]
				command = commands.delegate_command(cmd_name)
				commands.validate_command_args(command, args)
				self.reply_msg = command(args)
				
			except commands.CommandException as ex:
				self.reply_msg = ("%s - There was an error while attempting that command: %s"
								  	% (self.sender_name, ex.args[0]))
		
		# TODO else check for regex
		
	def reply(self, msg=None):
		"""
		Send a reply to the received message. If no message is given, reply with saved value from last call to parse().
		
		Args:
			msg (str, optional): the message to send in reply.
		"""
		
		raise NotImplementedError("reply() has not been implemented")


def set_up():
	"""
	Set up implementation-agnostic things.
	"""
	
	config_handler.load_all_configs()
	commands.register_commands()
