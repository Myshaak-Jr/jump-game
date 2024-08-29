import time
from typing import Any


__all__ = [
	"info",
	"error",
	"warn",
	"disable",
	"enable"
]


_do_log = False


def _info(*args: Any) -> None:
	if not _do_log: return

	print(f"[{time.strftime('%H:%M:%S')}]: ", end='')
	print('\033[96m', end='')
	print(*args)
	print('\033[0m', end='')

def _error(*args: Any) -> None:
	if not _do_log: return

	print(f"[{time.strftime('%H:%M:%S')}]: ", end='')
	print('\033[91m', end='')
	print(*args)
	print('\033[0m', end='')

def _warn(*args: Any) -> None:
	if not _do_log: return

	print(f"[{time.strftime('%H:%M:%S')}]: ", end='')
	print('\033[93m', end='')
	print(*args)
	print('\033[0m', end='')

def _noop(*args: Any) -> None: pass

def info(*args: Any) -> None: ...
info = _noop

def error(*args: Any) -> None: ...
error = _noop

def warn(*args: Any) -> None: ...
warn = _noop


def disable() -> None:
	global _do_log, info, error, warn
	_do_log = False
	info = _noop
	error = _noop
	warn = _noop

def enable() -> None:
	global _do_log, info, error, warn
	_do_log = True
	info = _info
	error = _error
	warn = _warn