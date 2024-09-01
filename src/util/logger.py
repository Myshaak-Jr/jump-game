import sys
import time
import traceback
from typing import Any, overload


__all__ = [
	"info",
	"error",
	"warn",
	"disable",
	"enable"
]


_do_log = False


def _info(*args: Any) -> None:
	print(f"[{time.strftime('%H:%M:%S')}]: ", end='')
	print('\033[96m', end='')
	print(*args)
	print('\033[0m', end='')

@overload
def _error(arg: Exception) -> None: ...

@overload
def _error(arg: Any, *args: Any) -> None: ...

def _error(arg: Any, *args: Any) -> None:
	print('\033[0m', end='', file=sys.stderr)

	print(f"[{time.strftime('%H:%M:%S')}]: ", file=sys.stderr, end='')
	print('\033[91m', end='', file=sys.stderr)

	if isinstance(arg, Exception):
		traceback.print_exception(type(arg), arg, arg.__traceback__)
	else:
		print(arg, *args, file=sys.stderr)
	
	
	print('\033[0m', end='', file=sys.stderr)
	print('\033[0m', end='')

def _warn(*args: Any) -> None:
	print(f"[{time.strftime('%H:%M:%S')}]: ", end='')
	print('\033[93m', end='')
	print(*args)
	print('\033[0m', end='')

def _noop(*args: Any) -> None: pass
def _noop2(arg: Any, *args: Any) -> None: pass

def info(*args: Any) -> None: ...
info = _noop


@overload
def error(arg: Exception) -> None: ...

@overload
def error(arg: Any, *args: Any) -> None: ...

def error(arg: Any, *args: Any) -> None: ...
error = _noop2

def warn(*args: Any) -> None: ...
warn = _noop


def disable() -> None:
	global _do_log, info, error, warn
	_do_log = False
	info = _noop
	error = _noop2
	warn = _noop

def enable() -> None:
	global _do_log, info, error, warn
	_do_log = True
	info = _info
	error = _error
	warn = _warn