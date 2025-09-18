"""
Configuration package for the Trading Intelligence application.
"""

from .app_config import get_config, AppConfig

# Import load_config from the parent config.py file using absolute import
import importlib.util
import os

# Get the path to the parent config.py file
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.py')
spec = importlib.util.spec_from_file_location("parent_config", config_path)
parent_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parent_config)

# Import the load_config function
load_config = parent_config.load_config

__all__ = ['get_config', 'AppConfig', 'load_config']