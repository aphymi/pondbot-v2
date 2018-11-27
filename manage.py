#!/usr/bin/python3
from importlib import import_module
import logging
import os
import subprocess
import sys
import unittest

import config
from exceptions import BotRestartException, BotShutdownException

imp_table = { # Human-friendly names mapped to class locations.
	"terminal": ("imps.terminal_bot", "TerminalBot"),
	"discord":  ("imps.discord_bot", "DiscordBot"),
}

arg_detach = "run"
arg_nodetach = "keep"
arg_kill =   "kill"
arg_configs = "make-configs"
arg_runtests = "test"

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
			# TODO Turn off all library logging.
			logging.basicConfig(filename="pb.log", level="WARNING")
			
			# Load the implementation chosen in the general config.
			config.load_config("general")
			imp = config.configs["general"]["implementation"]
			if imp not in imp_table:
				print("Unknown implementation: '%s'" % imp)
				print("Please specify a valid implementation in configs/general.yml")
				print("Valid implementations are: " + ", ".join(imp_table.keys()))
			
			bot_module, bot_class = imp_table[imp]
			Bot = getattr(import_module(bot_module), bot_class)
			
			try:
				Bot().run()
			
			except BotRestartException:
				print("Bot restarting")
				logging.info("Bot ordered to restart.")
				# First arg is file to run, second arg is C-style name of the command as first argument to process.
				os.execl("manage.py", "manage.py", arg_nodetach)
			
			except BotShutdownException:
				print("Bot shutting down")
				logging.info("Bot ordered to shut down.")
			
			except Exception as ex:
				logging.exception("An exception was encountered.")
		
		# Run the bot and detach from it immediately.
		elif command == arg_detach:
			subprocess.Popen([__file__, arg_nodetach],
							 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		
		# Stop any running instances of the bot.
		# This should only be used if the bot won't respond to commands.
		elif command == arg_kill:
			# TODO Find something more specific and less likely to kill other processes.
			print("Killing processes may have adverse effects. Only continue if you have no other way to stop the bot.")
			confirm = ""
			while confirm.lower() not in ("y", "n"):
				confirm = input("Are you sure you wish to proceed (y/n)? ")
			
			if confirm.lower() == "y":
				os.system("kill $(ps aux | grep '[m]anage.py keep' | awk '{print $2}')")
				print("Kill attempted.")
		
		elif command == arg_configs:
			config.make_defaults()
		
		elif command == arg_runtests:
			unittest.TextTestRunner(stream=sys.stdout) \
				.run(unittest.defaultTestLoader.discover("tests")) # Look for all tests in the 'tests' package.
			
		else:
			print("Unknown command.")
			print(usage)
