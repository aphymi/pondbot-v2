"""
Miscellaneous commands that aren't for a larger feature of the bot.

Commands:

"""

import random
import re

from plugins.commands import Command, CommandException


MAX_ROLL_AMOUNT = 20  # The maximum number of dice that can be rolled in one call to roll(), to prevent spam/slowing.
MAX_COMPLEX_SIDES = 999 # Maximum sides for a complex roll, to prevent spam.
mult_roll_re = re.compile(r"^(?P<arg1>\d+)(d(?P<cmplx_sides>\d+)(?P<modifier>[+-]\d+)?)?$")

# Args get joined in order to allow spaces.
@Command(args_val=(lambda *args: mult_roll_re.match("".join(args))),
		 args_usage="<sides>|<amount>d<sides>[<+|-><mod>]")
def roll(*args):
	"""
	Roll some dice.
	
	In a simple roll, there is only a single argument, one integer. <sides>
	In a complex roll, multiple dice are being rolled, possibly with a modifier.
	"""
	
	args = mult_roll_re.match("".join(args)).groupdict()
	
	# If the second argument isn't included, it's a simple roll.
	simple = args["cmplx_sides"] is None
	
	if simple:
		sides = int(args["arg1"])
		amount = 1
		mod = 0
	else:
		sides = int(args["cmplx_sides"])
		amount = int(args["arg1"])
		mod = 0 if not args["modifier"] else int(args["modifier"])
	
	# Argument errors.
	if amount > MAX_ROLL_AMOUNT: # Too many dice gets spammy, *way* too many sides gets slow.
		raise CommandException("You cannot roll more than %s dice." % MAX_ROLL_AMOUNT)
	if amount > 1 and sides > MAX_COMPLEX_SIDES: # Too many sides gets spammy.
		raise CommandException("Dice cannot have more than %s sides when rolling multiple dice." % MAX_COMPLEX_SIDES)
	if amount == 0:
		raise CommandException("You cannot roll 0 dice.")
	if sides < 2:
		raise CommandException("Dice must have at least 2 sides.")
	
	rolls = []
	for i in range(amount):
		rolls.append(random.randint(1, sides))
		
	result = str(sum(rolls)+mod)
	
	if not simple:
		# Put the modifier into string form, adding a plus first if it's positive. Empty string if mod is 0.
		if mod < 0:
			mod_str = str(mod)
		elif mod > 0:
			mod_str = "+" + str(mod)
		else:
			mod_str = ""
		
		return "({rolls}){mod} = {result}".format(rolls="+".join([str(r) for r in rolls]), mod=mod_str, result=result)
	
	return result

@Command(cooldown=5, args_val=(lambda *args: len(args) > 1), args_usage="<choice1> <choice2> [choice3]...")
def choose(*args):
	return "My choice is: " + random.choice(args)


# This args_val function means that the argument list must not be empty.
@Command(args_val=(lambda *args: args), args_usage="<text>")
def echo(*args):
	"""
	Repeat back whatever text is given.
	"""
	
	return " ".join(args)


@Command(args_val=(lambda *args: args), args_usage="<name>")
def welcome(*name):
	"""
	Welcome a new member of the server.
	"""
	
	# Join the name in case it contains a space.
	return "Everyone please welcome {} to the server!".format(" ".join(name))


# TODO Allow no space in !temp argument, like '36F' for !temp.
@Command(args_val=(lambda *args: len(args) == 2 and args[1].lower() in ("c", "f")),
		 args_usage="<degrees> <C|F>")
def temp(degrees, units):
	"""
	Convert between Celsius and Fahrenheit.
	
	Args:
		degrees -- Magnitude of temperature.
		units ---- Units that degrees are expressed in.
	"""
	
	try:
		degrees = float(degrees)
	except ValueError:
		raise CommandException("Could not parse degrees: %s" % degrees)
	
	if units.lower() == "c":
		return "{} in Celsius is {} in Fahrenheit.".format(degrees, round(degrees*(9/5) + 32, 1))
	
	elif units.lower() == "f":
		return "{} in Fahrenheit is {} in Celsius.".format(degrees, round((degrees-32) * (5/9), 1))
	
	else:
		raise CommandException("Unknown degree format: %s" % units)
