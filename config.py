"""
Module to handle loading of configuration files.
"""

import os
from os.path import join
from shutil import copyfile
import yaml

from handlers import fire_conf_load

configs = {}

def load_all_configs():
	"""
	Load all configuration files.
	"""
	
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
	
	with open(join("configs", (conf + ".yml"))) as file:
		config = yaml.load(file.read())
	
	fire_conf_load(config)
	configs[conf] = config


def make_defaults():
	"""
	Create configuration files for any default configurations in configs/.
	
	A default configuration file is defined as having a ".yml.def" extension.
	"""
	
	for file in os.listdir(join("configs", "defs")):
		root, ext = os.path.splitext(file)
		if ext == ".def": # If the file is a default file for a config.
			if not os.path.isfile(join("configs", root)):
				# If there is no manifested version of the default, create one.
				copyfile(join("configs", "defs", file), join("configs", root))
