"""
Translate messages from a Minecraft bridge to the bot's format.
"""

import re

import config
from handlers import messagehandler

@messagehandler
def mc_msg_handler(msg, _):
	conf = config.configs["minecraft"]
	
	sender = msg.sender_id or msg.sender_name
	if sender == conf["mc-bridge-name"]:
		m = re.match(conf["mc-bridge-form"], msg.text_content)
		if m:
			match = m.groupdict()
			msg.sender_name = match["NAME"]
			msg.text_content = match["MESSAGE"]
			rank = match.get("RANK")
			if rank:
				for group, ranks in conf["perm-groups"]:
					if rank in ranks:
						msg.sender_group = group
						break
