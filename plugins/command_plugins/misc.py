"""
Miscellaneous commands that aren't part of a larger feature of the bot.

Commands:
	roll <sides>|<dice>d<sides>[<+|-><mod>]
	choose <choice1> <choice2> [choice...]
	echo <text>
	welcome <name>
	temp <degrees> <C|F>
"""

import random
import re
from urllib.parse import urlencode

from plugins.commands import Command, CommandException
# The maximum number of dice that can be rolled in one call to roll(), to
# prevent spam/overloading the processor. The latter isn't much of a concern
# until at least the millions, though.
MAX_ROLL_AMOUNT = 20

# Maximum sides for a complex roll, to prevent spam.
MAX_COMPLEX_SIDES = 999

mult_roll_re = re.compile(
	r"^(?P<amount>\d+)d(?P<sides>\d+)(?P<modifier>[+-]\d+)?$"
)


@Command(
	args_val=(lambda *args:
		(
			len(args) == 1
			and args[0].isdigit()
		)
		or mult_roll_re.match("".join(args))
	),
	args_usage="<sides>|<amount>d<sides>[<+|-><mod>]",
)
def roll(*args):
	"""
	Roll some dice.
	
	In a simple roll, there is only a single argument; one integer which is the
	number of sides.
	In a complex roll, multiple dice are being rolled, possibly with a modifier.
	"""
	
	# Args get joined in order to allow spaces, e.g. '2 d8'.
	# Has a side effect of joining numbers separated by a space, but that's fine.
	args = "".join(args)
	simple = args.isdigit()
	
	# If the second argument isn't included, it's a simple roll.
	
	if simple:
		sides = int(args)
		amount = 1
		mod = 0
	else:
		args = mult_roll_re.match(args).groupdict()
		sides = int(args["sides"])
		amount = int(args["amount"])
		mod = 0 if not args["modifier"] else int(args["modifier"])
	
	# Argument errors.
	if amount > MAX_ROLL_AMOUNT:
		# Too many dice gets spammy, *way* too many dice gets slow.
		raise CommandException(
			f"You cannot roll more than {MAX_ROLL_AMOUNT} dice.",
		)
		
	if amount > 1 and sides > MAX_COMPLEX_SIDES:
		# Too many sides gets spammy.
		raise CommandException(
			f"Dice cannot have more than {MAX_COMPLEX_SIDES} sides when "
			"rolling multiple dice."
		)
		
	if amount == 0:
		raise CommandException("You cannot roll 0 dice.")
	
	if sides < 2:
		raise CommandException("Dice must have at least 2 sides.")
	
	rolls = []
	for i in range(amount):
		rolls.append(random.randint(1, sides))
		
	result = str(sum(rolls) + mod)
	
	if not simple:
		# Put the modifier into string form, adding a '+' first if it's
		# positive. Empty string if mod is 0.
		if mod < 0:
			mod_str = str(mod)
		elif mod > 0:
			mod_str = "+" + str(mod)
		else:
			mod_str = ""
	
		rolls = "+".join(str(r) for r in rolls)
		
		return f"({rolls}){mod_str} = {result}"
	
	return result


@Command(
	args_val=(lambda *args: len(args) > 1),
	args_usage="<choice1> <choice2> [choice...]",
)
def choose(*args):
	"""
	Randomly choose one of the arguments.
	"""
	
	return "My choice is: " + random.choice(args)


# This args_val function means that the argument list must not be empty.
@Command(args_val=(lambda *args: args), args_usage="<text>")
def echo(*args):
	"""
	Repeat back whatever text is given.
	"""
	
	return " ".join(args)


# TODO Allow no space in !temp argument, like '36F' for !temp.
@Command(
	args_val=(lambda *args: len(args) == 2 and args[1].lower() in ("c", "f")),
	args_usage="<degrees> <C|F>",
)
def temp(degrees, units):
	"""
	Convert between Celsius and Fahrenheit.
	
	Args:
		degrees: Magnitude of temperature.
		units: Units that degrees are expressed in.
	"""
	
	try:
		degrees = float(degrees)
	except ValueError:
		raise CommandException("Could not parse degrees: %s" % degrees)
	
	if units.lower() == "c":
		degrees_f = round(degrees * (9 / 5) + 32, 1)
		return f"{degrees} in Celsius is {degrees_f} in Fahrenheit."
	
	elif units.lower() == "f":
		degrees_c = round((degrees - 32) * (5 / 9), 1)
		return f"{degrees} in Fahrenheit is {degrees_c} in Celsius."
	
	else:
		raise CommandException("Unknown degree format: %s" % units)


@Command(args_val=(lambda *args: args), args_usage="<search term>")
def lmgtfy(*search):
	"""
	Get the LMGTFY link for the given text.
	
	Args:
		*search: the text to search for
	"""
	
	return "http://lmgtfy.com?" + urlencode({"q": " ".join(search)})
