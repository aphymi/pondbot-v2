from unittest import TestCase
import yaml

import permissions
from permissions import PermNode


class TestPermTrie(TestCase):
	
	def test_trie_simple_eq(self):
		self.assertTrue(PermNode(root=True) == PermNode(root=True))
		self.assertTrue(
			PermNode("a", tvalue=False) == PermNode("a", tvalue=False)
		)
		self.assertFalse(
			PermNode("a", tvalue=True) == PermNode("a", tvalue=False)
		)
	
	def test_add_perm_to_empty_trie(self):
		added_trie = PermNode.new()
		added_trie.add_perm("a")
		self.assertEquals(
			added_trie,
			PermNode(
				root=True,
				children={
					"a": PermNode("a", tvalue=True),
				},
			),
		)
		
		added_trie = PermNode.new()
		added_trie.add_perm("a.b.c")
		manual_trie = PermNode(
			root=True,
			children={
				"a": PermNode(
					"a",
					children={
						"b": PermNode(
							"b",
							children={
								"c": PermNode("c", tvalue=True)
							},
						),
					},
				),
			},
		)
		
		self.assertEquals(added_trie, manual_trie)
	
	def test_add_perm_to_nonempty_trie(self):
		added_trie = PermNode(root=True, children={"a": PermNode("a")})
		added_trie.add_perm("a.b")
		manual_trie = PermNode(
			root=True,
			children={
				"a": PermNode(
					"a",
					children={
						"b": PermNode("b", tvalue=True)
					},
				),
			},
		)
		
		self.assertEquals(added_trie, manual_trie)

		added_trie = PermNode(root=True, children={"a": PermNode("a")})
		added_trie.add_perm("c.d")
		manual_trie = PermNode(
			root=True,
			children={
				"a": PermNode("a"),
				"c": PermNode(
					"c",
					children={
						"d": PermNode("d", tvalue=True)
					},
				),
			},
		)
		
		self.assertEquals(added_trie, manual_trie)
	
	def test_add_negative_perm(self):
		added_trie = PermNode.new()
		added_trie.add_perm("-a")
		self.assertEquals(
			added_trie,
			PermNode(
				root=True,
				children={"a": PermNode("a", tvalue=False)},
			),
		)
		
		added_trie = PermNode.new()
		added_trie.add_perm("-a.b.c")
		manual_trie = PermNode(
			root=True,
			children={
				"a": PermNode(
					"a",
					children={
						"b": PermNode(
							"b",
							children={
								"c": PermNode("c", tvalue=False)
							},
						),
					},
				),
			},
		)
		
		self.assertEquals(added_trie, manual_trie)
		
	def test_nonconflicting_basic_merge(self):
		perms1 = [
			"a.b.c",
			"b.q.l",
			"a.l.x",
			"a.b.j",
		]
		perms2 = [
			"a.d.q",
			"a.b.d",
			"b.j.q",
			"c.a.b",
		]
		trie1 = PermNode.new()
		trie2 = PermNode.new()
		triec = PermNode.new()
		
		for perm in perms1:
			trie1.add_perm(perm)
			triec.add_perm(perm)
		
		for perm in perms2:
			trie2.add_perm(perm)
			triec.add_perm(perm)
		
		trie1.merge(trie2)
		self.assertEqual(trie1, triec)
	
	def test_merge_higher_group_pri_into_wildcard(self):
	
		lower = PermNode(root=True, group_lvl=1)
		lower.add_perm("a.*", group_lvl=1)
		
		higher = permissions.PermNode(root=True)
		higher.add_perm("a.b")
		
		lower.merge(higher)
		self.assertTrue(lower.has_perm("a.absent"))
		

class TestGroupPermissions(TestCase):
	
	def assertGHP(self, group, perm):
		self.assertTrue(
			permissions.group_has_perm(group, perm),
			msg=f"Group '{group}' does not have perm '{perm}', but should.",
		)
	
	def assertNotGHP(self, group, perm):
		self.assertFalse(
			permissions.group_has_perm(group, perm),
			msg=f"Group '{group}' has perm '{perm}', but should not."
		)
	
	@classmethod
	def setUpClass(cls):
		permissions.construct_perm_tries(
			yaml.load(fixture, Loader=yaml.FullLoader)
		)
	
	def test_root_wildcard(self):
		self.assertGHP("dev", "absent.nope.nada")
		self.assertNotGHP("muted", "absent.nope.nada")
	
	def test_nested_wildcard(self):
		self.assertGHP("default", "cmd.absent")
		self.assertNotGHP("nocmds", "cmd.absent")
		
	def test_absent_perm(self):
		self.assertNotGHP("default", "absent.nope.nada")
	
	def test_atomic_perm(self):
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
