from exceptions import BotShutdownException, BotRestartException
from plugins.commands import Command


@Command(args_val=(lambda *args: not args), args_usage="")
def shutdown():
	# print("But... I thought you loved me.)
	raise BotShutdownException

@Command(args_val=(lambda *args: not args), args_usage="")
def restart():
	# print("I'll come back better than ever!")
	raise BotRestartException
