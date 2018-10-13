"""
An implementation of PondBot for a simple terminal using only stdin and stdout.
"""

from bot import Message, Bot
from exceptions import BotShutdownException


class TerminalBot(Bot):
	"""
	A bot implementation involving only stdin and stdout.
	"""
	
	def run(self):
		self.set_up()
		
		while True:
			msg = input("> ")
			if msg.lower() == "quit":
				raise BotShutdownException
			msg = TerminalMessage(msg)
			
			msg.reply()

bot = TerminalBot


class TerminalMessage(Message):
	"""
	Class for working with Messages from a terminal.
	"""
	
	def __init__(self, msg):
		self.raw_msg = msg
		self.sender_name = "TERMINAL"
		self.sender_group = "devs"
		self.text_content = msg
		self.reply_msg = None
		
		self._parse()
	
	def reply(self):
		if self.reply_msg:
			print(self.reply_msg)
