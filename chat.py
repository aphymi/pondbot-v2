import errno
import logging
import os
import shutil
import yaml


class Message:
	"""
	Abstract class for working with messages.
	"""
	
	def get_text(self):
		"""
		Retrieve the text content of the message.
		
		Returns (str): the text content of the message.
		"""
		
		raise NotImplementedError("get_text() has not been implemented")
	
	def get_sender(self):
		"""
		Retrieve the text name of the person who sent the message.
		
		Returns (str): name of the sender.
		"""
		
		raise NotImplementedError("get_sender() has not been implemented")
	
	def reply(self, msg):
		"""
		Send a reply to the received message.
		
		Args:
			msg (str): the message to send in reply.
		"""
		
		raise NotImplementedError("reply() has not been implemented")


def parse(msg):
	"""
	Parse and potentially reply to a single message.
	Args:
		msg (Message): the received message.
	"""
	
	msg.reply("%s:%s" % (msg.get_sender(), "".join(reversed(msg.get_text()))))


def set_up():
	"""
	Set up implementation-agnostic things.
	"""
	
	pass


def load_config(config, default_location=None):
	"""
	Load one of the configs.
	
	Args:
		config (str): the name of the config to load in configs/ (e.g. "commands" for commands.yml).
		default_location (str, optional): the location of the default file for this config, relative to pondbot-v2/.
			Defaults to None.

	Returns (dict|list): A dictionary or list representing the contents of the chosen config file.
	
	If *default* is not specified but *config* doesn't exist, a FileNotFoundError will be raised.
	"""
	
	config_location = "configs/%s.yml" % config
	
	# Check if the config exists.
	if not os.path.isfile(config_location):
		logging.debug("Config '%s' not found; looking for default.", config)
		
		# If not, just copy the default over, and everything's peachy.
		if default_location:
			if os.path.isfile(default_location):
				shutil.copyfile(default_location, config_location)
				logging.debug("Config '%s' created from default.", config)
			else:
				# If the *default* doesn't exist, raise a scary exception.
				raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), default_location)
			
		else:
			# If no default was given, we're out of luck.
			raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), config_location)
	
	# At this point, if the config didn't exist before, it does now.
	with open(config_location) as file:
		return yaml.load(file)
