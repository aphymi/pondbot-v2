#!/usr/bin/python3
import logging
import os
import sys

import config_handler
from exceptions import BotRestartException, BotShutdownException
# TODO Figure out a better way to specify implementation to use.
# Select chat module to use.
from imps.terminal import bot as bot_imp

if __name__ == "__main__":
	usage = "Usage: manage.py <run|kill|keep|make-configs>"
	
	# sys.argv will look something like ['./manage.py', 'start'],
	#   so the specified command should be at sys.argv[1]
	if len(sys.argv) < 2:
		print("Please specify a command.")
		print(usage)
	else:
		command = sys.argv[1]
		
		# Run the bot, but don't detach from it.
		#   This way the running terminal will still get sysout.
		if command == "keep":
			# TODO Properly configure logging.
			logging.basicConfig(filename="pb.log", level="DEBUG")
			
			while True: # Loop to allow continued running if an exception arises.
				try:
					bot = bot_imp.bot()
					bot.run()
				
				except BotRestartException:
					logging.info("Bot ordered to restart.")
					continue
				
				except BotShutdownException:
					logging.info("Bot ordered to shut down.")
					break
				
				except Exception:
					logging.exception()
					break
		
		# Run the bot and detach from it immediately.
		elif command == "run":
			os.system("./manage.py keep &") # TODO Change this to a subprocess call (creationflags=DETACHED_PROCESS)
		
		# Stop any running instances of the bot.
		# This should only be used if the bot won't respond to commands.
		elif command == "kill": # TODO Add a y/n confirmation and warning to kill
			# TODO Figure out whether this should be run or keep
			os.system("kill $(ps aux | grep '[m]anage.py run' | awk '{print $2}')")
		
		elif command == "make-configs":
			config_handler.make_defaults()
			pass
		
		# TODO Make a reset-config command to replace a config with the default.
		
		else:
			print("Unknown command.")
			print(usage)
