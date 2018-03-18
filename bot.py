import config_handler
import commands
from exceptions import CommandException

# TODO 'Expansions' module? Use to get title and such from YT links.
# TODO Decide if imps need their own package, or can just be changed to e.g. terminal_bot.py

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
				commands.validate_command_args(command, args, cmd_name)
				self.reply_msg = command(*args)
				
			except CommandException as ex:
				self.reply_msg = ("{user} - That command caused an error: {errmsg}".format(
								  	user=self.sender_name, errmsg=ex.args[0]))
		
		# TODO else check for regex
		
	def reply(self):
		"""
		Send a reply to the received message.
		"""
		
		raise NotImplementedError("reply() has not been implemented")


def set_up():
	"""
	Set up implementation-agnostic things.
	"""
	
	config_handler.load_all_configs()
	commands.register_commands()
