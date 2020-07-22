#!/usr/bin/python3.6
"""
Executable for starting and running the bot.
"""


from importlib import import_module
import logging
import os
import subprocess
import sys
import unittest

import config
from exceptions import BotRestartException, BotShutdownException


# Human-friendly names mapped to class locations.
imp_table = {
	"terminal": ("imps.terminal_bot", "TerminalBot"),
	"discord": ("imps.discord_bot", "DiscordBot"),
}

arg_names = {
	"detach": "run",
	"nodetach": "keep",
	"kill": "kill",
	"configs": "make-configs",
	"runtests": "test",
}

if __name__ == "__main__":
	usage = f"Usage: manage.py <{'|'.join(arg_names.values())}>"
	
	# sys.argv will look something like ['./manage.py', 'start'],
	#   so the specified command should be at sys.argv[1]
	if len(sys.argv) < 2:
		print(
			"Please specify a command.",
			usage,
			sep="\n",
		)
		
	else:
		command = sys.argv[1]
		
		if command == arg_names["nodetach"]:
			# Run the bot, but don't detach from it.
			# If run by the user, the running terminal will still get sysout.
			logging.basicConfig(filename="pb.log", level="WARNING")
			
			# Load the implementation chosen in the general config.
			config.load_config("general")
			imp = config.configs["general"]["implementation"]
			
			if imp not in imp_table:
				print(
					f"Unknown implementation: '{imp}'",
					"Please specify a valid implementation in "
					+ "configs/general.yml",
					"List of valid implementations: "
					+ ', '.join(imp_table.keys()),
					sep="\n"
				)
			
			bot_module, bot_class = imp_table[imp]
			Bot = getattr(import_module(bot_module), bot_class)
			
			try:
				Bot().run()
			
			except BotRestartException:
				print("Bot restarting")
				logging.info("Bot ordered to restart.")
				
				os.execl(
					# The file to run.
					"manage.py",
					# C-style name of the command, as first argv.
					"manage.py",
					arg_names["nodetach"],
				)
			
			except BotShutdownException:
				print("Bot shutting down")
				logging.info("Bot ordered to shut down.")
			
			except Exception as ex:
				logging.exception("An exception was encountered.")
		
		# Run the bot and detach from it immediately.
		elif command == arg_names["detach"]:
			subprocess.Popen(
				[__file__, arg_names["nodetach"]],
				stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT,
			)
		
		# Stop any running instances of the bot.
		# This should only be used if the bot won't respond to commands.
		elif command == arg_names["kill"]:
			print(
				"Killing processes may have adverse effects. Only continue if "
				+ "you have no other way to stop the bot."
			)
			confirm = ""
			while confirm.lower() not in ("y", "n"):
				confirm = input("Are you sure you wish to proceed (y/n)? ")
			
			if confirm.lower() == "y":
				os.system(
					"kill "
					+ "$(ps aux | grep '[m]anage.py keep' | awk '{print $2}')"
				)
				print("Kill attempted.")
		
		elif command == arg_names["configs"]:
			config.make_defaults()
		
		elif command == arg_names["runtests"]:
			(
				unittest.TextTestRunner(stream=sys.stdout)
				.run(unittest.defaultTestLoader.discover("tests"))
			)
			
		else:
			print("Unknown command", usage, sep="\n")
