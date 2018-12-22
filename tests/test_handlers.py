from unittest import TestCase

from handlers import MessageHandler, ConfigLoadHandler

def nothing(_):
	pass

def msg_swap_case(msg):
	return msg.swapcase()

quack = "QUACK!"
def msg_quack(msg):
	if msg.startswith("quack"):
		return quack


class TestMessageHandler(TestCase):
	fire = MessageHandler.fire_handlers
	swap_msg = "aBcDeFOObar"
	quack_msg = "quackisquack"
	noquack_msg = "noquack"
	
	def setUp(self):
		MessageHandler.handlers.clear()
	
	def test_msg_handler_does_not_change_object(self):
		self.assertIs(nothing, MessageHandler(nothing))
		self.assertIs(msg_swap_case, MessageHandler(msg_swap_case))
		self.assertIs(msg_quack, MessageHandler(msg_quack))

	def test_zero_handlers_gives_no_resp(self):
		self.assertIsNone(self.fire(None))
	
	def test_empty_handler_gives_no_resp(self):
		MessageHandler(nothing)
		self.assertIsNone(self.fire(None))
	
	def test_certain_handler_gives_resp(self):
		MessageHandler(msg_swap_case)
		self.assertIsNotNone(self.fire(self.swap_msg))
		self.assertIsNotNone(self.fire(""))
	
	def test_uncertain_handler_conditionally_gives_resp(self):
		MessageHandler(msg_quack)
		self.assertIsNone(self.fire(self.noquack_msg))
		self.assertIsNotNone(self.fire(self.quack_msg))
	
	def test_handlers_give_expected_resp(self):
		MessageHandler(msg_swap_case)
		self.assertEqual(self.swap_msg.swapcase(), self.fire(self.swap_msg))
		MessageHandler.handlers.clear()
		MessageHandler(msg_quack)
		self.assertEqual(quack, self.fire(self.quack_msg))
	
	def test_empty_handler_yields_to_certain_handler(self):
		MessageHandler(nothing)
		MessageHandler(msg_swap_case)
		self.assertEqual(self.swap_msg.swapcase(), self.fire(self.swap_msg))
	
	def test_uncertain_handler_yields_to_succeeding_certain_handler_conditionally(self):
		MessageHandler(msg_quack)
		MessageHandler(msg_swap_case)
		self.assertEqual(quack, self.fire(self.quack_msg))
		self.assertEqual(self.swap_msg.swapcase(), self.fire(self.swap_msg))
	

def cl_val_data(new_conf):
	if "badkey" in new_conf:
		raise Exception("There's a badkey.")

has_run = set()
def cl_set_external_var(var_name):
	def handler(_):
		has_run.add(var_name)
	return handler

def cl_modify_conf(new_conf):
	new_conf["newkey"] = True

def cl_error_if_nonempty_conf(new_conf):
	if new_conf:
		raise Exception("The conf isn't empty!")

confA = "confA"
confB = "confB"

class TestConfigLoadHandler(TestCase):
	
	fire = ConfigLoadHandler.fire_handlers
	
	def setUp(self):
		ConfigLoadHandler.handlers.clear()
		has_run.clear()
		
	def test_malformed_conf_raises_error(self):
		ConfigLoadHandler(confA)(cl_val_data)
		self.assertRaisesRegex(Exception, "badkey", self.fire, confA, ["badkey"])
	
	def test_handler_gets_run(self):
		ConfigLoadHandler(confA)(cl_set_external_var("var"))
		self.assertNotIn("var", has_run)
		self.fire(confA, None)
		self.assertIn("var", has_run)
	
	def test_handler_modifies_new_conf(self):
		conf = {}
		ConfigLoadHandler(confA)(cl_modify_conf)
		self.assertNotIn("newkey", conf)
		self.fire(confA, conf)
		self.assertIn("newkey", conf)
		self.assertEquals(conf["newkey"], True)
		
	def test_handler_lastingly_modifies_new_conf(self):
		conf = {}
		ConfigLoadHandler(confA)(cl_modify_conf)
		ConfigLoadHandler(confA)(cl_error_if_nonempty_conf)
		self.assertNotIn("newkey", conf)
		self.assertRaisesRegex(Exception, "isn't empty", self.fire, confA, conf)
	
	def test_only_conf_specific_handlers_are_called_when_handlers_fired(self):
		ConfigLoadHandler(confA)(cl_set_external_var("var1"))
		ConfigLoadHandler(confB)(cl_set_external_var("var2"))
		
		self.fire(confA, None)
		self.assertIn("var1", has_run)
		self.assertNotIn("var2", has_run)
		
		has_run.clear()
		self.fire(confB, None)
		self.assertNotIn("var1", has_run)
		self.assertIn("var2", has_run)
	
	def test_multiple_handlers_on_one_conf(self):
		ConfigLoadHandler(confA)(cl_set_external_var("var1"))
		ConfigLoadHandler(confA)(cl_set_external_var("var2"))
		
		self.assertNotIn("var1", has_run)
		self.assertNotIn("var2", has_run)
		
		self.fire(confA, None)
		self.assertIn("var1", has_run)
		self.assertIn("var2", has_run)
	
	def test_multiple_handlers_on_multiple_confs(self):
		ConfigLoadHandler(confA)(cl_set_external_var("var1"))
		ConfigLoadHandler(confA)(cl_set_external_var("var2"))
		ConfigLoadHandler(confB)(cl_set_external_var("var3"))
		ConfigLoadHandler(confB)(cl_set_external_var("var4"))
		
		for i in (1, 2, 3, 4):
			self.assertNotIn("var" + str(i), has_run)
		
		self.fire(confA, None)
		self.assertIn("var1", has_run)
		self.assertIn("var2", has_run)
		self.assertNotIn("var3", has_run)
		self.assertNotIn("var4", has_run)
		
		has_run.clear()
		self.fire(confB, None)
		self.assertNotIn("var1", has_run)
		self.assertNotIn("var2", has_run)
		self.assertIn("var3", has_run)
		self.assertIn("var4", has_run)
	
	


