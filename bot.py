import config
from handlers import MessageHandler

# TODO Some kind of setup_handler? For stuff that needs to be done on bot startup, like loading data files.

class Bot:
	"""
	Abstract class for the chat bot.
	"""
	
	_cur_bot = None
	
	@staticmethod
	def set_up():
		"""
		Set up implementation-agnostic things.
		"""
		
		config.load_all_configs()
		
		for plugin in config.configs["general"]["plugins"]:
			__import__("plugins." + plugin)
		
		# Reload plugins one more time, since all config load handlers should be known by now.
		config.load_all_configs()
	
	def run(self):
		"""
		Perform whatever work is needed in order to start and run the bot.
		"""
		
		raise NotImplementedError("run() has not been implemented")
	
	@classmethod
	def bot(cls):
		"""
		Return the currently running Bot instance.
		"""
		
		return cls._cur_bot


class Message:
	"""
	Abstract class for working with messages.
	"""
	
	def __init__(self):
		# Raw data that the bot recieves at an implementation level.
		self.raw_msg = None
		# The eventual string that the bot will reply to this message with, if any.
		self.reply_msg = None
		# The name of the user that sent this message.
		self.sender_name = None
		# Optionally, a user-unique id for the user who sent this message.
		# Only necessary if sender_name is not necessarily unique for each user.
		self.sender_id = None
		# Optionally, the permission group that the user belongs to.
		self.sender_group = None
		# The text of the message that the user sent, with any other data stripped.
		self.text_content = None
	
	def _parse(self):
		"""
		Parse and do whatever work necessary for the message.
		
		If the message necessitates a reply, save it to self.reply_msg.
		"""
		
		self.reply_msg = MessageHandler.fire_handlers(self)
		
	def reply(self):
		"""
		Send a reply to the received message.
		"""
		
		raise NotImplementedError("reply() has not been implemented")
