"""
Simple cooldown functions.
"""

import datetime

_cooldowns = {}
# TODO Stop cooldowns dict from growing indefinitely


def has_cooled_down(key):
	"""
	Return True if the cooldown has expired or the key was never given a cooldown. False otherwise.

	Arguments:
	key -- Key that may have been previously registered with set_cooldown.
	"""
	
	return key not in _cooldowns or datetime.datetime.now() >= _cooldowns[key]


def set_cooldown(key, seconds=0, forever=False):
	"""
	Set a cooldown on the given key for the given amount of time.

	Arguments:
	key ------ Key that can be checked later for expiration of cooldown using has_cooled_down().
	seconds -- Amount of seconds to wait before the cooldown expires.
	forever -- True if the cooldown should never expire. False otherwise.
	"""
	
	if forever:
		_cooldowns[key] = datetime.datetime.max
	else:
		_cooldowns[key] = datetime.datetime.now() + datetime.timedelta(seconds=seconds)


def remove_cooldown(key):
	"""
	Remove the cooldown on the given key, if it has one.
	
	Arguments:
		key -- Key to remove the cooldown of.
	"""
	
	if key in _cooldowns:
		del _cooldowns[key]
