"""
An implementation of PondBot for a simple terminal.
"""

from bot import Message, Bot, set_up
from exceptions import BotShutdownException



class TerminalBot(Bot):
	"""
	A bot implementation involving only stdin and stdout.
	"""
	
	def run(self):
		set_up()
		
		while True:
			msg = input("> ")
			if msg.lower() == "quit":
				raise BotShutdownException
			msg = TerminalMessage(msg)
			
			if msg.reply_msg is not None:
				msg.reply()

bot = TerminalBot


class TerminalMessage(Message):
	"""
	Class for working with Messages from a terminal.
	"""
	
	def __init__(self, msg):
		self.raw_msg = msg
		self.text_content = msg
		self.sender_name = "TERMINAL USER"
		self.reply_msg = None
		
		self._parse()
	
	def reply(self):
		print(self.reply_msg)
