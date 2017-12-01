"""
Manage chat command interactions in the bot.
"""

import functools


class Command:
	"""
	Used as a decorator to define command objects.
	
	Attributes:
		static (bool) ------ If True, this command is static. If False, it is dynamic.
		
		cooldown (number) -- The mimimum time (in seconds) between when a command was last used,
				and when it can be used again.
				
		args_val (func) ---- A function to be run and given the list of command arguments as a parameter.
				When the arguments are syntactically valid for the command, it returns True. False otherwise.
				
		args_usage (str) --- A string describing the syntactic form of arguments to this command.
	
	A static command is one which always replies with the same value, regardless of arguments or other context.
	Static and dynamic commands are disjoint and all-encompassing.
	"""
	
	def __init__(self, static=False, cooldown=5, args_val=lambda args: True, args_usage=""):
		self.static = static
		self.cooldown = cooldown
		self.args_val = args_val
		self.args_usage = args_usage
	
	def __call__(self, cmd):
		"""
		Call the wrapped command, returning its reply.
		
		Args:
			cmd: The wrapped command.

		Returns: A str containing the command's reply to the arguments, or None if there is no reply.

		"""
		@functools.wraps(cmd)
		def wrapped_func(args=[]):
			if self.static:
				# Don't bother passing any received arguments.
				args.clear()
			
			return cmd(*args)
		
		wrapped_func.meta = self.meta
		# TODO Here, add self to list of dynamic commands.
		return wrapped_func
