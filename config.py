"""
Module to handle loading of configuration files.
"""

import os
from shutil import copyfile
import yaml

configs = {}

def load_all_configs():
	"""
	Load all configuration files.
	"""
	
	configs.clear()
	
	for file in os.listdir("configs/"):
		# Split the file into the root and its extension.
		root, ext = os.path.splitext(file)
		if ext == ".yml":
			load_config(root)
	
		
def load_config(conf):
	"""
	Load or reload a specific configuration file.
	Args:
		conf -- the file to load, without the extension.
	"""
	
	with open(os.path.join("configs", (conf + ".yml"))) as file:
		configs[conf] = yaml.load(file.read())


def make_defaults():
	"""
	Create configuration files for any default configurations in configs/.
	
	A default configuration file is defined as having a ".yml.def" extension.
	"""
	
	for file in os.listdir("configs/"):
		if file.endswith(".yml.def"):
			conf = file[:-8] # Truncate the file extension.
			if not os.path.isfile("configs/%s.yml" % conf):
				# This config doesn't exist, so copy it over.
				copyfile("configs/%s.yml.def" % conf, "configs/%s.yml" % conf)
