#!/usr/bin/python3
import os
import sys

# Select chat module to use.
from imps.terminal import bot as chat_imp

if __name__ == "__main__":
	usage = "Usage: ./manage.py <run|kill|keep>"
	
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
			chat_imp.run_bot()
		
		# Run the bot and detach from it immediately.
		elif command == "run":
			os.system("./manage.py keep &") #TODO Change this to a subprocess call (creationflags=DETACHED_PROCESS)
		
		# Stop any running instances of the bot.
		# This should only be used if the bot won't respond to commands.
		elif command == "kill":
			os.system("kill $(ps aux | grep '[m]anage.py runkeep' | awk '{print $2}')")
		
		else:
			print("Unknown command.")
			print(usage)
