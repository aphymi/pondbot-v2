from unittest import TestCase
import yaml

import permissions


class TestPermissions(TestCase):
	
	def assertGHP(self, group, perm):
		self.assertTrue(permissions.group_has_perm(group, perm),
		                msg="Group '{}' does not have perm '{}', but should.".format(group, perm))
	
	def assertNotGHP(self, group, perm):
		self.assertFalse(permissions.group_has_perm(group, perm),
		                 msg="Group '{}' has perm '{}', but should not.".format(group, perm))
	
	@classmethod
	def setUpClass(cls):
		permissions.construct_perm_tries(yaml.load(fixture))
	
	def test_positive_wildcard(self):
		self.assertGHP("dev", "absent.nope.nada")
	
	def test_negative_wildcard(self):
		self.assertNotGHP("muted", "absent.nope.nada")
	
	def test_nested_positive_wildcard(self):
		self.assertGHP("default", "cmd.absent")
	
	def test_nested_negative_wildcard(self):
		self.assertNotGHP("nocmds", "cmd.absent")
		
	def test_absent_perm(self):
		self.assertNotGHP("default", "absent.nope.nada")
	
	def test_basic_perm(self):
		self.assertGHP("default", "fred")
		self.assertNotGHP("default", "thud")
	
	def test_nested_perm(self):
		self.assertGHP("default", "baz.bork")
		self.assertNotGHP("default", "foo.bar")
	
	def test_specific_perm_overrides_wildcard(self):
		self.assertGHP("default", "regex.trigger")
		self.assertNotGHP("default", "cmd.kick")
		
	def test_specific_perm_overrides_multiple_wildcards(self):
		self.assertGHP("default", "a.b.c")
		self.assertNotGHP("default", "a.b.d.e")
		self.assertGHP("default", "f.g.h")
		self.assertNotGHP("default", "i.j.k")
	
	def test_group_perm_overrides_inherited_perm(self):
		self.assertGHP("mod", "foo.bar")
		self.assertNotGHP("mod", "regex.trigger")
	
	def test_inherited_wildcard_with_nonconflicting_group_perm(self):
		self.assertGHP("mod", "l.absent")
	
	def test_group_perm_overrides_inherited_wildcard(self):
		self.assertGHP("mod", "f.b")
		self.assertNotGHP("mod", "a.c")
	
	def test_group_wildcard_overrides_inherited_perm(self):
		self.assertGHP("mod", "foo.absent")
		self.assertNotGHP("mod", "baz.absent")
	
	def test_merge_higher_group_pri_into_wildcard(self):
		# This never happens during normal group processing, since
		# 	lower priority tries are always merged into higher priority tries,
		# 	and never the other way around.
	
		lower = permissions.PermNode(root=True, group_lvl=1)
		lower.add_perm("a.*", group_lvl=1)
		
		higher = permissions.PermNode(root=True)
		higher.add_perm("a.b")
		
		lower.merge(higher)
		self.assertTrue(lower.has_perm("a.absent"))


# yaml-formatted permission config.
fixture = """
groups:
  default:
    perms:
    - cmd.*
    - -cmd.shutdown
    - -cmd.restart
    - -cmd.kick
    - -cmd.ban
    - regex.trigger
    - -regex.*
    - fred
    - -thud
    - baz.bork
    - -foo.bar
    - a.*
    - -a.b.*
    - a.b.c
    - a.b.d.*
    - -a.b.d.e
    - -f.*
    - -f.g.*
    - f.g.h
    - i.*
    - i.j.*
    - -i.j.k
    - l.*

  mod:
    inherit:
    - default
    perms:
    - -regex.trigger
    - cmd.kick
    - cmd.ban
    - cmd.echo
    - foo.bar
    - foo.*
    - -baz.*
    - -a.c
    - f.b
    - l.a.b

  admin:
    inherit:
    - mod
    perms:
    - -regex.trigger
    - '*'

  dev:
    perms:
    - '*'

  muted:
    perms:
    - '-*'

  nocmds:
    perms:
    - -cmd.*
"""
