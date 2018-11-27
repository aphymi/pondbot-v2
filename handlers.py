_msg_handlers = []
_conf_handlers = {}


def messagehandler(handler_func):
	"""
	Decorator for functions that should be run whenever the bot receives a message.
	
	All such handlers should accept exactly two arguments:
		msg -- the Message object produced when the bot receives a message.
		ctx -- any other non-message-specific context, e.g. the Bot object of the current imp.
	
	Handlers may modify the msg/ctx args freely, and later-fired handlers will recieve the changed versions.
	
	A handler may return a string, in which case it is assumed that event doesn't need further handling,
		and no further handlers need be called. The bot will reply to the message with the string.
	
	"""
	
	_msg_handlers.append(handler_func)
	return handler_func

def fire_msg(msg, ctx=None):
	"""
	Notify messagehandlers of an incoming message.
	Args:
		msg -- the Message object associated with the incoming message.
		ctx -- any other relevant context the handlers should have.
	
	Returns:
		reply (str) -- if any events give a reply to the message, that reply will be returned as a string.
	"""
	
	for handler in _msg_handlers:
		rep = handler(msg, ctx)
		if rep:
			return rep


def confighandler(conf_name):
	"""
	Decorator for functions that should run whenever a config is reloaded.
	
	All such handlers should accept exactly one argument:
		new_conf -- the decoded YAML of the new version of the config.
	
	Handlers may modify conf freely, and later-fired handlers will recieve the changed version.
	
	Args:
		conf_name:

	Returns:

	"""
	
	def confhandler(handler_func):
		if conf_name not in _conf_handlers:
			_conf_handlers[conf_name] = []
		_conf_handlers[conf_name].append(handler_func)
		return handler_func
	
	return confhandler
	
def fire_conf_load(conf_name, new_conf):
	"""
	Notify confighandlers of a reloaded config.
	Args:
		conf_name -- the name of the config being reloaded (e.g. 'general' or 'commands').
		new_conf --- the decoded YAML of the new version of the config.
	"""
	
	for handler in _conf_handlers.get(conf_name, []):
		handler(new_conf)
