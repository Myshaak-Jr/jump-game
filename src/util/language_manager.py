"""This module handles localization of the application."""
import os
from . import logger as log


_languages: dict[str, dict[str, str]] = {}
_current_language = None

def init() -> None:
	"""Loads the languages."""
	PATH = "assets/lang/"
	for file in os.listdir(PATH):
		if file.endswith(".lang"):
			with open(PATH + file, "r") as f:
				_languages[file[:-5]] = dict([line.strip().replace("\\n", "\n").split("=") for line in f.readlines() if line.strip() and not line.strip().startswith("#")])

def get(key: str) -> str:
	"""Returns the localized string for the given key."""
	if _current_language is None:
		raise ValueError("No language set")
	
	if key not in _languages[_current_language]:
		log.warn(f"Key '{key}' not found in language '{_current_language}'")

	return _languages[_current_language].get(key, key)

def set_language(language: str) -> None:
	"""Sets the current language."""
	global _current_language
	_current_language = language

def get_current_language() -> str:
	"""Returns the current language."""
	return _current_language

def get_languages() -> list[str]:
	"""Returns the available languages."""
	return list(_languages.keys())

