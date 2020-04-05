"""
Commands that allow saving of memorable quotes.

Commands:
	quote <id>
	addquote <quote>
	remquote <id...>
	resquote <id...>
"""

import copy
from datetime import datetime
import json
import os
import random

import config
from exceptions import CommandException
from handlers import ConfigLoadHandler
from plugins.commands import Command


"""
The quote list is a dict with unique (linearly-generated) ids as the keys
and, as values, dicts with the following keys.

content: The literal quotation.
date: The date that the quote was added to the list.
display: Optional boolean to indicate whether a quote should be publicly
displayed. If 'preserve-deled-qs' is set to true, this property is set to false
when a quote is deleted.
"""
quotes = {}

# String path to the used quotes file
QUOTES_FILE = os.path.join(os.path.dirname(__file__), "quotes.json")


@ConfigLoadHandler("quotes")
def load_quote_list(_):
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
		quotes.update({
			int(k): v
			for k, v in json.load(file).items()
		})


def write_quotes():
	"""
	Write the quotes list to the quotes file.
	"""
	
	with open(QUOTES_FILE, "w") as file:
		json.dump(quotes, file, indent="\t")
	
	out_file = config.configs["quotes"]["quotelist"]["file"]
	if out_file is not None:
		quotes_clone = copy.deepcopy(quotes)
		
		for qid in list(quotes_clone.keys()):
			# Don't output any quotes that shouldn't be displayed.
			if not quotes_clone[qid]["display"]:
				del quotes_clone[qid]
			
			# Don't show the 'display' key in the output.
			else:
				del quotes_clone[qid]["display"]
		
		with open(out_file, "w") as file:
			json.dump(quotes_clone, file, indent="\t")


@Command(
	cooldown=15,
	args_val=(
		lambda *args: not args or (len(args) == 1 and args[0].isdigit())
	),
	args_usage="[quote id]",
)
def quote(qid=None):
	"""
	Print a quote from the quotes list.
	
	Args:
		qid: the id of the quote to view. If omitted, a random quote will be
		retrieved.
	"""
	
	if qid:
		qid = int(qid)
		if qid not in quotes or not quotes[qid].get("display", True):
			return "That quote isn't on the list."
	
	else:
		qs = {
			k: v
			for k, v in quotes.items()
			if v.get("display", True)
		}
		if not qs:
			return "The quote list is empty."
		
		qid = random.choice(list(qs.keys()))
	
	return "Quote #{}: {}".format(qid, quotes[qid]["content"])


@Command(args_val=(lambda *args: args), args_usage="<quote>")
def addquote(*text):
	"""
	Add a quote to the quotes list.
	
	Args:
		text: the text of the quote to be saved, as a string that's been split.
	"""
	
	qid = max(quotes) + 1 if quotes else 0
	quo = {
		"content": " ".join(text),
		"date": str(datetime.now()),
		"display": True,
	}
	
	quotes[qid] = quo
	write_quotes()
	return "Quote #%s saved." % qid


@Command(
	args_val=(lambda *args: args and all([arg.isdigit() for arg in args])),
	args_usage="<id...>",
)
def remquote(*nums):
	"""
	Remove one or more quotes from the quotes list.
	
	Args:
		*nums: the id of the quote to be deleted.
	
	If 'preserve-deled-qs' is set to true in the quotes config, quotes will be
	set to non-displayable, instead of deleted.
	"""
	
	pres = config.configs["quotes"]["preserve-deled-qs"]
	nums = [int(num) for num in nums]
	
	for num in nums:
		# If the specified number isn't in the quotes list, *or* (it is but set
		# to nondisplay *and* config is set to preserve deleted). In this way,
		# preserved quotes will only be permanently deleted if preserve has
		# since been set to false.
		quote_cant_display = (
			num not in quotes
			or (
				pres
				and not quotes[num].get("display", True)
			)
		)
		if quote_cant_display:
			raise CommandException(
				f"There isn't any quote #{num} on the list.",
			)
	
	for num in nums:
		if pres:
			quotes[num]["display"] = False
		else:
			del quotes[num]
	
	write_quotes()
	
	quote_numbers = ", ".join(f"#{num}" for num in nums)
	return f"Quote{'s' if len(nums) > 1 else ''} deleted: {quote_numbers}"


@Command(
	args_val=(lambda *args: args and all([arg.isdigit() for arg in args])),
	args_usage="<id...>",
)
def resquote(*nums):
	"""
	Restore one or more deleted quotes.
	
	Restoration of a quote is only possible if said quote was deleted while
	preservation was enabled in the quotes config.
	
	Args:
		*nums: a list of ids of quotes to be restored.
	"""

	nums = [
		int(num)
		for num in nums
	]
	
	for num in nums:
		if num not in quotes or quotes[num].get("display", True):
			raise CommandException(f"Quote #{num} is not restorable.")
	
	for num in nums:
		quotes[num]["display"] = True
	
	write_quotes()
	
	quote_numbers = ", ".join(f"#{num}" for num in nums)
	return f"Quote{'s' if len(nums) > 1 else ''} restored: {quote_numbers}"


@Command(args_val=(lambda *args: not args), args_usage="")
def quotelist(args=None):
	"""
	Get a link to the quote list, if such has been configured.
	"""

	url = config.configs["quotes"]["quotelist"]["url"]

	if url is None:
		return (
			"Sorry! The quotelist command is disabled. Configure it in "
			"configs/quotes.yml to enable it."
		)
	
	else:
		return url
