"""
Commands for interacting with the quotes of the late NexusBot.

Commands:
  xquote <id>
"""

import json
import os
import random

from exceptions import CommandException
from plugins.commands import Command

QUOTES_FILE = os.path.join(os.path.dirname(__file__), "xquotes.json")

quotes = []

with open(QUOTES_FILE, "r") as file:
	quotes[:] = json.load(file)


@Command(cooldown=15, args_val=(lambda *args: not args or (len(args) == 1 and args[0].isdigit())),
		args_usage="[quote id]")
def xquote(qid=None):
	if qid:
		qid = int(qid)
		if not 1 <= qid <= len(quotes):
			return "That quote isn't on the list."
	
	else:
		qid = random.randint(1, len(quotes))
	
	quote = quotes[qid-1]
	return "X-Quote #{}: {} (Saved by: {})".format(qid, quote["quote"], quote["poster"])
