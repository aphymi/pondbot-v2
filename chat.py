import errno
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


def load_config(config):
	"""
	Load one of the configs.
	
	Args:
		config (str): the name of the config to load (e.g. "commands" for commands.yml).

	Returns (dict|list): A dictionary or list representing the contents of the chosen config file.
	"""
	
	# Check if the config exists.
	if not os.path.isfile("configs/%s.yml" % config):
		# If it doesn't, check if there's a default for it.
		if os.path.isfile("configs/defaults/%s.yml" % config):
			# If so, copy the default over, and everything's peachy.
			shutil.copyfile("configs/defaults/%s.yml", "configs/%s.yml")
		else:
			# If not, raise a scary exception.
			raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), "%s.yml" % config)
	
	# At this point, either the config existed, or has now been generated from the default.
	with open("configs/%s.yml" % config) as file:
		return yaml.load(file)
