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
			msg = TerminalMessage(input("> "))
			msg.reply()

bot = TerminalBot


class TerminalMessage(Message):
	"""
	Class for working with Messages from a terminal.
	"""
	
	def __init__(self, msg):
		super().__init__()
		self.raw_msg = msg
		self.sender_name = "TERMINAL"
		self.sender_group = "default"
		self.text_content = msg
		
		self._parse()
	
	def reply(self):
		if self.reply_msg:
			print(self.reply_msg)
