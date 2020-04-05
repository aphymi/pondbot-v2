"""
React to messages which match certain regex.
"""

import re

import config
import cooldown
from handlers import MessageHandler, ConfigLoadHandler
from permissions import group_has_perm

# _regexes is a list containing a single re, instead of just a straight re,
#   because it needs to be mutable in order for inner scopes to assign to it.
_regexes = []
_resps = []


@ConfigLoadHandler("regex")
def compose_regexes(new_conf):
	"""
	Compose the set of regexes from the config.
	"""
	
	_regexes.clear()
	regs, _resps[:] = new_conf["statics"].keys(), new_conf["statics"].values()

	_regexes.append(
		re.compile(
			"|".join(f"({s})" for s in regs),
			flags=re.IGNORECASE,
		),
	)


@MessageHandler
def regex_msg_handler(msg):
	"""
	Trigger regex responses on appropriate messages.
	"""
	
	if not group_has_perm(msg.sender_group, "regex.trigger"):
		return
	
	m = _regexes[0].match(msg.text_content)
	
	if m:
		# Find which regex got matched.
		ind = None
		for ind, val in enumerate(m.groups()):
			if val:
				break

		# ind now equals the index of the first non-None value.
		cdk = f"regex.{ind}"
		if cooldown.has_cooled_down(cdk):
			cooldown.set_cooldown(
				cdk,
				config.configs["regex"]["static-cooldown"],
			)
			return f"{msf.sender_name} - {_resps[ind]}"
