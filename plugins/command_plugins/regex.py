from copy import copy

from exceptions import CommandException
from plugins.commands import Command
from plugins.regex import regex_msg_handler

@Command(args_val=(lambda *args: args), args_usage="<message>",
         pass_msg=True)
def regex(msg, *args):
	msg = copy(msg)
	msg.text_content = " ".join(args)
	msg.sender_group = "default" # TODO Make this not an awful hack.
	
	resp = regex_msg_handler(msg)
	
	if not resp:
		raise CommandException("No regex found.")

	return resp



