#!/usr/bin/python3
from importlib import import_module
import logging
import os
import subprocess
import sys

import config_handler
from exceptions import BotRestartException, BotShutdownException

imp_table = { # Human-friendly names mapped to class locations.
	"terminal": ("imps.terminal_bot", "TerminalBot"),
	"discord":  ("imps.discord_bot", "DiscordBot"),
}

arg_detach = "run"
arg_nodetach = "keep"
arg_kill =   "kill"
arg_configs = "make-configs"

if __name__ == "__main__":
	usage = "Usage: manage.py <{}|{}|{}|{}>".format(arg_detach, arg_nodetach, arg_kill, arg_configs)
	
	# sys.argv will look something like ['./manage.py', 'start'],
	#   so the specified command should be at sys.argv[1]
	if len(sys.argv) < 2:
		print("Please specify a command.")
		print(usage)
	else:
		command = sys.argv[1]
		
		# Run the bot, but don't detach from it.
		#   If run by the user, the running terminal will still get sysout.
		if command == arg_nodetach:
			# TODO Properly configure logging.
			logging.basicConfig(filename="pb.log", level="DEBUG")
			
			# Load the implementation chosen in the general config.
			config_handler.load_config("imp")
			imp = config_handler.configs["imp"]["implementation"]
			if imp not in imp_table:
				print("Unknown implementation: '%s'" % imp)
				print("Please specify a valid implementation in configs/imp.yml")
				print("Valid implementations are: " + ", ".join(imp_table.keys()))
			
			bot_module, bot_class = imp_table[imp]
			Bot = getattr(import_module(bot_module), bot_class)
			
			while True: # Loop to allow continued running if an exception arises.
				try:
					Bot().run()
				
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
		elif command == arg_detach:
			subprocess.Popen([__file__, arg_nodetach],
							 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		
		# Stop any running instances of the bot.
		# This should only be used if the bot won't respond to commands.
		elif command == arg_kill: # TODO Add a y/n confirmation and warning to kill
			# TODO Find something more specific and less likely to kill other processes.
			os.system("kill $(ps aux | grep '[m]anage.py keep' | awk '{print $2}')")
		
		elif command == arg_configs:
			config_handler.make_defaults()
			pass
		
		# TODO Make a reset-config command to replace a config with the default.
		
		else:
			print("Unknown command.")
			print(usage)
