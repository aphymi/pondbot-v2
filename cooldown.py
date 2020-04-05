"""
Module for simple cooldown functions.
"""

import datetime

_cooldowns = {}


def has_cooled_down(key):
	"""
	Return whether the given key has cooled down.
	
	True if the cooldown has expired or the given key hasn't been put on
	cooldown, and False otherwise.
	
	Args:
		key: key that may have been previously registered with set_cooldown.
	"""
	
	return key not in _cooldowns or datetime.datetime.now() >= _cooldowns[key]


def set_cooldown(key, seconds=0, forever=False):
	"""
	Set a cooldown on the given key for the given amount of time.

	Arguments:
		key: key that can be checked later for expiration of cooldown.
		seconds: amount of seconds to wait before the cooldown expires.
		forever: true if the cooldown should never expire. False otherwise.
	"""
	
	if forever:
		_cooldowns[key] = datetime.datetime.max
		
	else:
		_cooldowns[key] = (
			datetime.datetime.now()
			+ datetime.timedelta(seconds=seconds)
		)


def remove_cooldown(key):
	"""
	Remove the cooldown on the given key, if it has one.
	
	Arguments:
		key: key to remove the cooldown of.
	"""
	
	if key in _cooldowns:
		del _cooldowns[key]
