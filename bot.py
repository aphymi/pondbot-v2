import config
import handlers


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
		self.raw_msg = None
		self.reply_msg = None
		self.text_content = None
		self.sender_name = None
	
	def _parse(self):
		"""
		Parse and do whatever work necessary for the message.
		
		If the message necessitates a reply, save it to self.reply_msg.
		"""
		
		self.reply_msg = handlers.fire_msg(self)
		
	def reply(self):
		"""
		Send a reply to the received message.
		"""
		
		raise NotImplementedError("reply() has not been implemented")
