from copy import deepcopy

from handlers import confighandler


# TODO Add a config option to specify a default group.
# TODO Presently, the behavior of conflicting perms like 'a.b' and '-a.b.*' is undefined. Define it.
# TODO Get rid of group_lvl concept, and just run a BFS on the inheritance graph.

class PermNode:
	"""
	A single node of a permission trie for a single permission group.

	Attributes:
		name ------- the name of this specific node, e.g. "cmd" or "foo", but not "cmd.foo".
		root ------- boolean of whether this is the root node in the perm trie.
		tvalue ----- the truth value of this specific node, either True, False, or None.
		wildcard --- boolean of whether all descendants should have the same tvalue as this node.
		children --- child nodes of this permission node.
		group_lvl -- the priority of the permission group that this node originally came from.
	
	There are two semantically different types of nodes; terminal and intermediate nodes.
	
	Terminal nodes are those resulting from being the last node of a parsed permission, e.g. "c" in "a.b.c".
	They are distinguished by having a non-None tvalue, and represent possible stopping points
		in perm resolution. Their tvalue is False if the perm is negated, and True otherwise.
	
	Intermediate nodes are those that were not the last node of any parsed permission, e.g. "a" and "b" in "a.b.c".
	They are distinguished by their tvalue being None, and represent intermediate points in perm resolution.
	"""

	WILDCARD_NAME = "*" # Wildcard node gives/negates all descendants if they are not otherwise specified..
	PERM_SEP = "." # Separator for the individual nodes of a permission string, e.g. in "foo.bar.baz".
	NEG_PREFIX = "-" # Prefix that indicates a permission is negated.
	
	def __init__(self, name="", root=False, tvalue=None,
				 wildcard=None, children=None, group_lvl=0):
		
		self.name = name
		self.root = root
		self.tvalue = tvalue
		self.wildcard = wildcard
		self.children = children or {} # Can't just use normal default arg, since lists are mutable.
		self.group_lvl = group_lvl
	
	@property
	def child_vals(self):
		"""
		Retrieve the PermNodes of this node's children.
		
		Created for use with pptree.print_tree()
		"""
		
		return self.children.values()
	
	@property
	def formatted_name(self):
		"""
		Return a formatted string of this node's name and attributes.
		
		Created primarily for use with pptree.print_tree()
		
		>>> PermNode(name='foo').name
		'foo'
		
		>>> PermNode(name='bar', tvalue=False, wildcard=True).name
		'-bar*'
		
		"""
		
		return "{}{}{}".format("-" if self.tvalue is False else "",
							   self.name,
							   "*" if self.wildcard else "")
	
	def __str__(self):
		return "PermNode(name=%s, tvalue=%s%s)" % (self.formatted_name, "*" if self.wildcard else "", self.tvalue)
	
	__repr__ = __str__
	
	def __eq__(self, other):
		return all([getattr(self, attr) == getattr(other, attr) for attr in ("name", "root",
																			 "tvalue", "wildcard",
																			 "group_lvl", "children")])
	
	@classmethod
	def new(cls):
		return cls(root=True)
	
	def is_terminal(self):
		"""
		Return True if this is a terminal node, and False otherwise.
		"""
		
		return self.tvalue is not None
	
	def add_perm(self, perm, group_lvl=0):
		"""
		Add a single permission to this trie. This node must be the root.
		
		Args:
			perm ------- the permission string to add to the trie.
			group_lvl -- the group_lvl of perm.
		"""

		if not self.root:
			raise Exception("Cannot add a perm to a non-root trie node.")

		# If the perm starts with the negation prefix, set the tvalue to false and chop the prefix off.
		tvalue = not perm.startswith(self.NEG_PREFIX)
		if not tvalue:
			perm = perm[len(self.NEG_PREFIX):]

		# Walk until the perm is out of nodes.
		cur = self
		for name in perm.split(self.PERM_SEP):
			# This node is a wildcard; the previous node should be set accordingly.
			if name == self.WILDCARD_NAME:
				cur.wildcard = True
				break # Wildcards should only every be the last node in a perm, but just in case.
			
			# If the current perm node isn't in the trie node's children, make it.
			if name not in cur.children.keys():
				cur.children[name] = PermNode(name=name, group_lvl=group_lvl)
				
			# Otherwise, change the group_lvl to the lower of the two.
			else:
				cur.children[name].group_lvl = min(cur.children[name].group_lvl, group_lvl)
		
			cur = cur.children[name]

		cur.tvalue = tvalue

	def merge(self, other):
		"""
		Recursively merge another permission trie with self.
		
		Where both tries have a terminal node in the same place, take the values of the
			one with the higher group priority.
		
		Args:
			other -- the trie to merge with self.
		"""
		
		# Use other's tvalue if self isn't terminal or other has a higher priority.
		if not self.is_terminal() or (other.is_terminal() and self.group_lvl > other.group_lvl):
			self.tvalue = other.tvalue
		
		self.wildcard = self.wildcard or other.wildcard

		# Merge the children together.
		for name in other.children:
			# If there's already an equivalent node in self, merge the two.
			if name in self.children:
				self.children[name].merge(other.children[name])
			
			# Otherwise, just adopt it.
			else:
				self.children[name] = other.children[name]
	
	def has_perm(self, perm):
		"""
		Test whether self includes the given permission. This node must be the root.
		
		Args:
			perm -- the perm to test against this perm trie.
		
		Returns: True if self includes perm, False otherwise.
		"""

		if not self.root:
			raise Exception("Cannot verify a perm against a non-root trie node.")

		# Walk through the trie, looking for a satisfying node.
		max_pri = (float("-inf"), float("-inf"), False) # Default to False, if nothing found.
		cur = self
		level = 0

		for name in perm.split(self.PERM_SEP):
			# Set a new max_pri if the current node is a wildcard.
			if cur.wildcard:
				max_pri = max(max_pri, (-cur.group_lvl, level, cur.tvalue))
			
			# If we can continue the search, do so.
			if name in cur.children:
				level += 1
				cur = cur.children[name]
			
			# If we've reached the end of the trie without exhausting the perm,
			#   default to either the last wildcard, or the default value.
			else:
				break

		# If the loop didn't break, then the perm was exhausted.
		else:
			if cur.is_terminal():
				max_pri = max(max_pri, (-cur.group_lvl, level, cur.tvalue))

		return max_pri[2]
	
	def increment_group_lvl(self):
		"""
		Increment the group_lvl of every node in the trie.
		"""

		self.group_lvl += 1

		for node in self.children.values():
			node.increment_group_lvl()


perm_groups = {}

@confighandler("permissions")
def validate_perm_groups(conf):
	groups = conf["groups"]
	
	# If the default group isn't defined, make it.
	if "default" not in groups:
		groups["default"] = {}
	
	# Make sure no group inherits from a nonexistent group.
	for group in groups:
		for inh in groups[group].get("inherit", []):
			if inh not in groups:
				raise Exception("Permission group '%s' inherits from nonexistent group '%s'." % (group, inh))
	
	# Ensure there are no cycles in the inheritance graph.
	
	# Keep a record, so we don't go over nodes we've already checked.
	cleared = set()
	
	def cycle_search(node, past):
		"""
		Search for a cycle in the inheritance graph including this group or its descendants.
		Raise an exception if found.
		
		Args:
			group -- the current node.
			past --- a set of all nodes that have been encountered in the past.
		"""
		
		if node in past: # We've encountered this node before; we found a cycle.
			raise Exception("Permission inheritance loop including group '%s'." % node)
		
		if node in cleared: # We've already checked this node and its descendants elsewhere in the traversal.
			return None
		
		past.add(node)
		
		for desc in groups[node].get("inherit", []):
			cycle_search(desc, past)
		
		past.discard(node) # Pop the current item off the past stack.
		cleared.add(node) # Mark the current node as cleared.
	
	# Search every group for cycles.
	for group in groups:
		cycle_search(group, set())
	
	
def make_perm_trie(groups_conf, group):
	"""
	Make the perm trie for the given group.
	
	Args:
		group -- the name of the permission group to make a perm trie for.
	"""
	
	if group in perm_groups:
		return
	
	trie = perm_groups[group] = PermNode(root=True)
	for perm in groups_conf[group].get("perms", []):
		trie.add_perm(perm)
	
	for g in groups_conf[group].get("inherit", []):
		if g not in perm_groups:
			make_perm_trie(groups_conf, g)
		
		gt = deepcopy(perm_groups[g])
		gt.increment_group_lvl()
		
		trie.merge(gt)

@confighandler("permissions")
def construct_perm_tries(conf):
	
	# Clear the perm groups, in case this is a reload.
	perm_groups.clear()
	
	for group in conf["groups"]:
		make_perm_trie(conf["groups"], group)

			
def group_has_perm(group, perm):
	# If the user somehow has a non-specified permission group, assume false.
	if group not in perm_groups:
		return False
	
	return perm_groups[group].has_perm(perm)

