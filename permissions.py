import config
from handlers import confighandler


"""
Permission node rules:

Deeper values trump shallower values:
	if "x.*", but also "-x.y", then x.y is False.
	if "-x.*", but also "x.y.*", then "x.y.z" is True.
	And vice versa for both.


"""

# TODO Need to return True, False, or None for perm in perm tree
# Need to know if a perm is negated or just not specified, in case a perm is negated
# 	for a given perm group, but is non-negated for a group that inherits it.

_perm_trees = {}

class PermNode:
	"""
	A single node of a permission tree for a single permission group.

	Attributes:
		name ------- the name of this specific node, e.g. "cmd" or "foo", but not "cmd.foo".
		tvalue ----- the truth value of this specific node, either True, False, or None.
		children --- child nodes of this permission node.
		group_pri -- the priority of the permission group that this node originally came from.
	
	There are two semantically different types of nodes; terminal and intermediate nodes.
	
	Terminal nodes are those resulting from being the last name of a parsed permission, e.g. "c" in "a.b.c".
	They are distinguished by having a non-None tvalue and group_pri, and represent possible stopping points
	in perm resolution. Their tvalue is False if the perm is negated, and True otherwise.
	
	Intermediate nodes are those that were not the last name of any parsed permission, e.g. "a" and "b" in "a.b.c".
	They are distinguished by their tvalue and group_pri being None, and represent intermediate points in perm
	resolution.
	"""

	name = None
	tvalue = None
	children = []
	group_pri = None

	WILDCARD = "*" # Wildcard node gives/negates all siblings and their descendants.
	PERM_SEP = "." # Separator for the individual nodes of a permission string, e.g. in "foo.bar.baz".
	
	def __init__(self, name=None, tvalue=None, children=None, group_pri=None):
		self.name = name
		self.tvalue = tvalue
		self.children = children if children is not None else [] # Can't just use normal def, since lists are mutable.
		self.group_pri = group_pri
	
	def __str__(self):
		return "PermNode(name=%s, tvalue=%s)" % (self.name, self.tvalue)
	
	__repr__ = __str__
	
	@classmethod
	def tree_from_perm(cls, perm, group_pri, neg=False):
		"""
		TODO tree_from_perm docstring.
		"""
		
		if cls.PERM_SEP not in perm:
			return cls(name=perm, tvalue=(not neg), group_pri=group_pri)
		
		ind = perm.index(PermNode.PERM_SEP)
		return cls(perm[:ind], group_pri=group_pri, children=[cls.tree_from_perm(perm[ind+1:], group_pri, neg)])

	def merge(self, otree):
		"""
		TODO merge docstring.
		"""
		
		# If self's tvalue is None, use otree's (also-possibly-None) tvalue.
		# Even if not, if self's priority is lower than otree's, still use otree's tvalue
		if self.tvalue is None or self.group_pri < otree.group_pri:
			self.tvalue = otree.tvalue

		# Merge the children together.
		
		# First, construct a dict for quick O(1) access of children by name.
		child_inds = {c.name:i for i, c in enumerate(self.children)} # Maybe change this to a name:index of child dict?
		
		# Merge every one of otree's children into self.
		for ochild in otree.children:
			if ochild.name in child_inds:
				# Since there's already an equivalent node in self's children, merge the two.
				self.children[child_inds[ochild.name]].merge(ochild)
			
			else:
				# There's no equivalent node in self's children, so adopt it.
				self.children.append(ochild)

	def match_perm(self, perml, level):
		"""
		TODO blah

		Arguments:
			perml -- a list of names of the remaining permission nodes to search for.
			level -- the number of steps this node is from the root.

		Returns: a tuple (group_priority, -level, tvalue) representing the highest matched
				terminal permission node, among this node or its descendants.
		"""

		# TODO Make this less complicated, taking advantage of the fact there is only ever
		#   a maximum of two possible paths, and that only if there's a wildcard child.
		
		if not perml:
			# Parent was the perm's terminal node; no need to continue.
			return None
		
		if self.name == PermNode.WILDCARD:
			# Wildcard node should be held to a lower priority than its siblings,
			#   so subtract .5 from it.
			# Wildcard has no children and always has a non-None tvalue.
			return self.group_pri, -(level - .5), self.tvalue

		if self.name == perml[0]:
			# This node matches the current step in permission parsing.
			if len(perml) == 1 and self.tvalue is not None:
				# This node is the perm's terminal node and has a tvalue.
				return (self.group_pri, -level, self.tvalue)

			if len(perml) > 1:
				# We've not yet reached the perm's terminal node; keep going.
				# Return the highest-priority terminal node that can be found among the children.
				return min(filter(lambda x: x is not None,
								  [c.match_perm(perml[1:], level+1) for c in self.children]),
				           default=None)


@confighandler("permissions")
def construct_perm_trees(conf):
	pass
	

# TODO Once config reload handlers are a thing, just make a dict (str:set) of pre-resolved perms
#      for each perm group.
# TODO Better permission resolution algorithm.
#      Allow for negative nodes? Do breadth-first inheritance search?
#      Allow for arbitrary dot separation and *? Part of pre-resolution?
def get_perms(g):
	group = config.configs["permissions"]["groups"][g]
	
	# Yield this group's permissions.
	yield from group["perms"]
	
	# Yield permissions from all the groups this one inherits from. Goes depth-first.
	for igroup in group.get("inherit", []):
		yield from get_perms(igroup)

# At present time, all permissions should match /-?\w+\.(\w+|\*)/
# First character series is conventionally the permission's originating plugin name.
# Second series is the specific permission name, or an asterisk to represent free access to all of that
#   module's permissions.
def group_has_perm(gname, perm):
	# 'default' is a special group name, for when the user is not part of a group.
	if not gname:
		gname = "default"
	
	star = perm[:perm.index(".")] + ".*"
	perms_list = list(get_perms(gname))
	
	if "-"+star in perms_list or "-"+perm in perms_list:
		return False
	if star in perms_list or perm in perms_list:
		return True
	return False
