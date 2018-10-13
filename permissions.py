import config

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
