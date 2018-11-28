from plugins.commands import Command

@Command(args_val=(lambda *args: args), args_usage="<name>")
def welcome(*name):
	"""
	Welcome a new member of the server.
	"""
	
	# Join the name in case it contains a space.
	return "Everyone please welcome {} to the server!".format(" ".join(name))

# TODO Make the formatting on these commands less messy.

@Command(args_val=(lambda *args: len(args) == 1 and args[0].isdigit()),
		 args_usage="<# of items>")
def stacks(items):
	"""
	Find the number of stacks an item breaks down into.
	"""
	
	items = int(items)
	stacks, left = items // 64, items % 64
	
	return "{items} item{iplur} break{bplur} down into {stacks} stack{splur} with {left} item{niplur} left over." \
			.format(items=items,
					stacks=stacks,
					left=left,
					iplur="" if items == 1 else "s",
					bplur="s" if items == 1 else "",
					splur="" if stacks == 1 else "s",
					niplur="" if left == 1 else "s")


@Command(args_val=(lambda *args: len(args) == 1 and args[0].isdigit()),
         args_usage="<# of stacks>")
def items(stacks):
	"""
	Find the number of items in a number of stacks.
	"""
	
	stacks = int(stacks)
	items = stacks*64
	
	return "{stacks} stack{splur} break down into {items} item{iplur}." \
		.format(stacks=stacks,
				items=items,
				splur="" if stacks == 1 else "s",
				iplur="" if items == 1 else "s")
