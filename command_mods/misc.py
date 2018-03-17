"""
Miscellaneous commands that aren't for a larger feature of the bot.

Commands:

"""

import random
import re
import requests

from commands import Command, CommandException


MAX_ROLL_AMOUNT = 20 # The maximum number of dice that can be rolled in one call to roll()

# TODO: set a max on number of dice that can be rolled in command
# TODO: add negative modifier? Allow spaces?
# TODO: prevent nonsensical values (!roll 10d0)
# Can't give more descriptive names to arg1 and arg2, because the meanings can change.
# TODO: Figure out better names for arg1 & arg2
# TODO: Make all the args ints beforehand
# TODO: Add individual rolls for complex rolls.
mult_roll_re = re.compile(r"(?P<arg1>\d+)(d(?P<arg2>\d+)(\+(?P<modifier>\d+))?)?")


@Command(cooldown=5, args_val=(lambda args: len(args) == 1 and mult_roll_re.match(args[0])),
		 args_usage="<sides>|<amount>d<sides>[+<mod>]")
def roll(arg):
	
	args = mult_roll_re.match(arg).groupdict()
	simple = args["arg2"] is not None
	if args["arg2"] is None: # Simple roll
		sides = int(args["arg1"])
		amount = 1
		mod = 0
	else:
		sides = int(args["arg2"])
		amount = int(args["arg1"])
		if amount > MAX_ROLL_AMOUNT:
			raise CommandException("You tried to roll %s dice, while the maximum is %s." % (amount, MAX_ROLL_AMOUNT))
		mod = 0 if not args["modifier"] else int(args["modifier"])
	
	rolls = []
	for i in range(amount):
		rolls.append(random.randint(1, sides))
		
	return str(sum(rolls) + mod)
