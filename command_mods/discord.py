from commands import Command
from exceptions import BotShutdownException, BotRestartException


@Command(cooldown=5, args_val=(lambda *args: True), args_usage="")
def shutdown():
	# print("But... I thought you loved me.)
	raise BotShutdownException

@Command(cooldown=5, args_val=(lambda *args: True), args_usage="")
def restart():
	# print("I'll come back better than ever!")
	raise BotRestartException