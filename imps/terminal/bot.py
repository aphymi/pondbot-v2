"""
An implementation of PondBot for a simple terminal.
"""

from chat import Message, parse

def run_bot():
	"""
	Start the bot.
	"""
	
	while True:
		msg = input("> ")
		if msg == "quit":
			break
		message = TerminalMessage(msg)
		parse(message)


class TerminalMessage(Message):
	"""
	Class for working with Messages from a terminal.
	"""
	
	def __init__(self, msg):
		self.msg = msg
	
	def reply(self, msg):
		print(msg)
		
	def get_text(self):
		return self.msg
	
	def get_sender(self):
		return "TERMINAL"
