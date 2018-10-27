"""
Commands that allow saving of memorable quotes.

Commands:
  quote <id>
  addquote <quote>
  remquote <id...>
  resquote <id...>
"""

from datetime import datetime
import json
import os
import random

import config
from exceptions import CommandException
from handlers import confighandler
from plugins.commands import Command


"""
The quote list is a dict with unique (linearly-generated) ids as the keys
	and, as values, dicts with the following keys.

content -- The literal quotation.
date ----- The date that the quote was added to the list.
display -- Optional boolean to indicate whether a quote should be publicly displayed.
               If 'preserve-deled-qs' is set to true, this property is set to false whe a quote is deleted.
"""
quotes = {}

# String path to the used quotes file
QUOTES_FILE = os.path.join(os.path.dirname(__file__), "quotes.json")

@confighandler("quotes")
def load_quote_list(_=None):
	"""
	Load the quotes from the quote file and save them as quote_list.
	"""
	
	# If the file doesn't exist yet, create an empty one.
	if not os.path.isfile(QUOTES_FILE):
		write_quotes()
	
	with open(QUOTES_FILE, "r") as file:
		quotes.clear()
		# Writing dicts to json automatically converts int keys to strings.
		# We want them as ints, so undo that as it's read in.
		quotes.update({int(k):v for k,v in json.load(file).items()})


def write_quotes():
	"""
	Write the quotes list to the quotes file.
	"""
	
	with open(QUOTES_FILE, "w") as file:
		json.dump(quotes, file, indent="\t")

load_quote_list()


@Command(cooldown=15, args_val=(lambda *args: not args or (len(args) == 1 and args[0].isdigit())),
		 args_usage="[quote id]")
def quote(qid=None):
	"""
	Print a quote from the quotes list.
	
	Args:
		num -- the id of the quote to view. If omitted, a random quote will be retrieved.
	"""
	
	if qid:
		qid = int(qid)
		if qid not in quotes or not quotes[qid].get("display", True):
			return "That quote isn't on the list."
	
	else:
		qs = {k:v for k,v in quotes.items() if v.get("display", True)}
		if not qs:
			return "The quote list is empty."
		
		qid = random.choice(list(qs.keys()))
	
	return "Quote #{}: {}".format(qid, quotes[qid]["content"])


@Command(args_val=(lambda *args: args), args_usage="<quote>")
def addquote(*text):
	"""
	Add a quote to the quotes list.
	
	Args:
		text -- the text of the quote to be saved, as a string that's been .split().
	"""
	
	qid = max(quotes)+1 if quotes else 0
	quo = {"content": " ".join(text),
	       "date": str(datetime.now()),
	       "display": True}
	
	quotes[qid] = quo
	write_quotes()
	return "Quote #%s saved." % qid


@Command(args_val=(lambda *args: args and all([arg.isdigit() for arg in args])), args_usage="<id...>")
def remquote(*nums):
	"""
	Remove one or more quotes from the quotes list.
	
	Args:
		nums -- the id of the quote to be deleted.
	
	If 'preserve-deled-qs' is set to true in the quotes config, quotes will be set to non-displayable,
		instead of deleted.
	"""
	
	pres = config.configs["quotes"]["preserve-deled-qs"]
	nums = [int(num) for num in nums]
	
	for num in nums:
		# If the specified number isn't in the quotes list,
		#   *or* (it is but set to nondisplay *and* config is set to preserve deleted).
		# In this way, preserved quotes will only be permanently deleted if preserve has since
		#   been set to false.
		if num not in quotes or (pres and not quotes[num].get("display", True)):
			raise CommandException("There isn't any quote #%s on the list." % num)
		
	for num in nums:
		if pres:
			quotes[num]["display"] = False
		else:
			del quotes[num]
	
	write_quotes()
	return "Quote{} deleted: {}".format("s" if len(nums) > 1 else "",
										", ".join("#"+str(num) for num in nums))


@Command(args_val=(lambda *args: args and all([arg.isdigit() for arg in args])), args_usage="<id...>")
def resquote(*nums):
	"""
	Restore a quote that was deleted from the quotes list while preservation was set to true.
	
	Args:
		num -- The ID of the quote to be restored.
	"""

	nums = [int(num) for num in nums]
	
	for num in nums:
		if num not in quotes or quotes[num].get("display", True):
			raise CommandException("Quote #%s is not restorable." % num)
	
	for num in nums:
		quotes[num]["display"] = True
	
	write_quotes()
	return "Quote{} restored: {}".format("s" if len(nums) > 1 else "",
										", ".join("#"+str(num) for num in nums))
