"""
Classes for handler decorators.
"""


class Handler:
	"""
	Abstract class for decorating functions to handle certain events.

	Attrs:
		dec_takes_args: boolean of whether a given Handler subclass takes
			arguments in its decorator.
	
	For example, if NoArgsHandler has dec_takes_args set to False, it would be
	used like:
	@NoArgsHandler
	def foo():
		bar
	
	whereas if ArgsHandler has dec_takes_args set to True, it would be used
	instead like:
	@ArgsHandler("argument", "another arg")
	def baz():
		bork
	"""

	dec_takes_args = False
	
	handlers = None
	
	@staticmethod
	def __new__(cls, *args, **kwargs):
		"""
		Create a new object.
		"""
		
		# The only purpose of the decorator is to add the function to the
		# handler list, so creation of an actual object is not necessary when
		# the decorator is applied directly, without arguments. Add the handler
		# to the list and return it unchanged.
		if not cls.dec_takes_args:
			# Only possible first argument is the handler.
			cls.add_handler(args[0], *args[1:], **kwargs)
			return args[0]
		
		# Otherwise, create the object as normal.
		obj = super().__new__(cls)
		obj.initargs = args
		obj.initkwargs = kwargs
		return obj

	def __init__(self, *args, **kwargs):
		# Save the provided arguments, for when the decorater is __call__ed.
		assert self.dec_takes_args
		self.initargs = args
		self.initkwargs = kwargs

	def __call__(self, func):
		"""
		Call the instance.
		"""
		
		# Add the handler to the list and return it unchanged.
		assert self.dec_takes_args
		self.add_handler(func, *self.initargs, **self.initkwargs)
		return func
		
	@classmethod
	def add_handler(cls, *args, **kwargs):
		"""
		Append the passed handler to the list.
		"""

		cls.handlers.append(args[0])

	@classmethod
	def fire_handlers(cls, *args, **kwargs):
		"""
		Fire every handler, passing in any received arguments.
		"""

		for handler in cls.handlers:
			handler(*args, **kwargs)


class MessageHandler(Handler):
	"""
	Decorator for handlers which fire when the bot receives a message.
	
	MessageHandlers should accept one argument:
		msg: an instantiated imp-specific subclass of bot.Message representing
			the message the bot received.
	
	The msg parameter is passed by-reference, so mutations to it will be seen
	by later-fired handlers.
	
	A handler may return a non-None value to indicate that processing of a
	particular event is finished, and no further handlers should be called. If
	such a value is a string, the bot will use it to reply to the message which
	incited the event.
	"""

	dec_takes_arg = False

	handlers = []

	@classmethod
	def fire_handlers(cls, msg):
		"""
		Fire message handlers.
		
		Args:
			msg: the message which provoked the event.
		"""

		for handler in cls.handlers:
			resp = handler(msg)
			if resp is not None:
				return resp
		

class ConfigLoadHandler(Handler):
	"""
	Decorator for handlers which fire when a config file is [re]loaded.
	
	The decorator should be passed a single argument:
		conf_name: the name of the configuration file (without '.yml') that the
			handler should be alerted to.
	
	Each handler should accept a single argument:
		new_conf: the yaml-parsed contents of the newly updated config file.
	"""

	dec_takes_args = True

	handlers = {}

	@classmethod
	def add_handler(cls, handler, conf_name):
		"""
		Add a handler for a specific config.

		Args:
			handler: the handler to add.
			conf_name: name of the configuration file (minus '.py') that this
				handler should be alerted to.
		"""

		if conf_name not in cls.handlers:
			cls.handlers[conf_name] = []

		cls.handlers[conf_name].append(handler)
	
	@classmethod
	def fire_handlers(cls, conf_name, new_conf):
		"""
		Fire handlers for the given config.

		Args:
			conf_name : the name of the config being loaded.
			new_conf: the parsed contents of the new config file.
		"""

		for handler in cls.handlers.get(conf_name, []):
			handler(new_conf)
