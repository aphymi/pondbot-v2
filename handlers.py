
_msg_handlers = []

def messagehandler(handler_func):
	"""
	Decorator for functions that should be run whenever the bot receives a message.
	
	All such handlers should accept exactly two arguments:
		msg -- the Message object produced when the bot receives a message.
		ctx -- any other non-message-specific context, e.g. the Bot object of the current imp.
	
	Handlers may modify the msg/ctx args freely, and later-fired handlers will see the changed versions.
	
	If a handler returns anything (ususally a string), it is assumed that the handler has fully handled
		the event, and no further handlers need be called. Such a string will be included in the bot's reply.
	
	"""
	
	_msg_handlers.append(handler_func)
	return handler_func


def fire_msg(msg, ctx=None):
	"""
	Notify MessageHandlers of an incoming message.
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
