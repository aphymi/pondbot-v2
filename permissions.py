"""
Module for permission handling.
"""

from copy import deepcopy

from handlers import ConfigLoadHandler


class PermNode:
	"""
	A single node of a permission trie for a single permission group.

	Attributes:
		name: the name of this specific node, e.g. "cmd" or "foo", but not
			"cmd.foo".
		root: boolean of whether this is the root node in the perm trie.
		tvalue: the truth value of this specific node, either True, False, or
			None.
		wildcard: boolean of whether all descendants should have the same
			tvalue as this node.
		children: child nodes of this permission node.
		group_lvl: the priority of the permission group that this node
			originally came from.
	"""

	# The marker for the wildcard node, which gives/negates all descendants if
	# they are not otherwise specified.
	WILDCARD_NAME = "*"
	
	# The separator for the permission nodes in a single permission string.
	PERM_SEP = "."
	
	# The prefix which indicates that a permission node is negated.
	NEG_PREFIX = "-"
	
	def __init__(
		self,
		name="",
		root=False,
		tvalue=None,
		wildcard=None,
		children=None,
		group_lvl=0,
	):
		
		self.name = name
		self.root = root
		self.tvalue = tvalue
		self.wildcard = wildcard
		self.children = children or {}
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
		
		Examples:
			>>> PermNode(name='foo').name
			'foo'
			
			>>> PermNode(name='bar', tvalue=False, wildcard=True).name
			'-bar*'
		
		"""
		
		neg_prefix = "-" if self.tvalue is False else ""
		wildcard_suffix = "*" if self.wildcard else ""
		
		return f"{neg_prefix}{self.name}{wildcard_suffix}"
	
	def __str__(self):
		"""
		Convert the permission node to a string.
		"""
		
		wildcard = "*" if self.wildcard else ""
		return "PermNode(name={}, tvalue={}{}".format(
			self.formatted_name,
			"*" if self.wildcard else "",
			self.tvalue,
		)
	
	__repr__ = __str__
	
	def __eq__(self, other):
		"""
		Compare the equality of all PermNode attributes.
		"""
		
		eq_attrs = [
			"name",
			"root",
			"tvalue",
			"wildcard",
			"group_lvl",
			"children",
		]
		
		return all(
			getattr(self, attr) == getattr(other, attr)
			for attr in eq_attrs
		)
	
	@classmethod
	def new(cls):
		"""
		Make a new PermNode root object.
		"""
		
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
			perm: the permission string to add to the trie.
			group_lvl: the group level of perm.
		"""

		if not self.root:
			raise Exception("Cannot add a perm to a non-root trie node.")

		# If the perm starts with the negation prefix, set the tvalue to false
		# and remove the prefix.
		tvalue = not perm.startswith(self.NEG_PREFIX)
		if not tvalue:
			perm = perm[len(self.NEG_PREFIX):]

		# Walk the trie until the perm is out of nodes.
		cur = self
		for name in perm.split(self.PERM_SEP):
			# This node is a wildcard; the previous node should be set
			# accordingly.
			if name == self.WILDCARD_NAME:
				cur.wildcard = True
				# Wildcards should only every be the last node in a perm, but
				# we'll break just in case.
				break
			
			# If the current perm node isn't in the trie node's children, add
			# it.
			if name not in cur.children.keys():
				cur.children[name] = PermNode(name=name, group_lvl=group_lvl)
				
			# Otherwise, change the group_lvl to the lower of the two.
			else:
				cur.children[name].group_lvl = min(
					cur.children[name].group_lvl,
					group_lvl,
				)
		
			cur = cur.children[name]

		cur.tvalue = tvalue

	def merge(self, other):
		"""
		Recursively merge another permission trie with self.
		
		Where both tries have a terminal node in the same place, take the
		values of the one with the higher group priority.
		
		Args:
			other: the trie to merge with self.
		"""
		
		# Use other's tvalue if self isn't terminal or other has a higher
		# priority.
		use_other_tvalue = (
			not self.is_terminal()
			or (
				other.is_terminal()
				and self.group_lvl > other.group_lvl
			)
		)
		if use_other_tvalue:
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
		Test whether self includes the given permission.
		
		Args:
			perm: the perm to test against this perm trie.
		
		Returns: True if self includes perm, False otherwise.
		"""

		if not self.root:
			raise Exception(
				"Cannot verify a perm against a non-root trie node."
			)

		# Walk through the trie, looking for a satisfying node.
		
		# Default to False, if nothing is found.
		max_pri = (float("-inf"), float("-inf"), False)
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


@ConfigLoadHandler("permissions")
def validate_perm_groups(conf):
	"""
	Validate the loaded config.
	
	Args:
		conf: the config to validate.
	"""
	
	groups = conf["groups"]
	
	# If the default group isn't defined, make it.
	if "default" not in groups:
		groups["default"] = {}
	
	# Make sure no group inherits from a nonexistent group.
	for group in groups:
		for inh in groups[group].get("inherit", []):
			if inh not in groups:
				raise Exception(
					f"Permission group '{group}' inherits from nonexistent "
					+ f"group '{inh}'."
				)
	
	# Ensure there are no cycles in the inheritance graph.
	
	# Keep a record, so we don't go over nodes we've already checked.
	cleared = set()
	
	def cycle_search(node, past):
		"""
		Search for a cycle in the inheritance graph.
		
		An exception is raised if one is found.
		
		Args:
			node: the current node.
			past: a set of all nodes that have been encountered in the past.
		"""
		
		if node in past:
			# We've encountered this node before; we found a cycle.
			raise Exception(
				f"Permission inheritance loop including group '{node}'."
			)
		
		if node in cleared:
			# We've already checked this node and its descendants elsewhere in
			# the traversal.
			return None
		
		past.add(node)
		
		for desc in groups[node].get("inherit", []):
			cycle_search(desc, past)
		
		# Pop the current item off the past stack.
		past.discard(node)
		# Mark the current node as cleared.
		cleared.add(node)
	
	# Search every group for cycles.
	for group in groups:
		cycle_search(group, set())
	
	
def make_perm_trie(groups_conf, group):
	"""
	Make the perm trie for the given group.
	
	Args:
		groups_conf: the config to create the perm trie with.
		group: the name of the permission group to make a perm trie for.
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


@ConfigLoadHandler("permissions")
def construct_perm_tries(conf):
	"""
	Construct perm tries from the given config.
	
	Args:
		conf: the config to construct perm tries from.
	"""
	
	# Clear the perm groups, in case this is a reload.
	perm_groups.clear()
	
	for group in conf["groups"]:
		make_perm_trie(conf["groups"], group)

			
def group_has_perm(group, perm):
	"""
	Return true if the given group has the given perm, or False otherwise.
	
	Args:
		group: the group to test for permission inclusion.
		perm: the perm to test.
	"""
	
	if group is None:
		# Give the default group if no other is specified.
		group = "default"
	
	# If the user somehow has a non-specified permission group, assume false.
	if group not in perm_groups:
		return False
	
	return perm_groups[group].has_perm(perm)
