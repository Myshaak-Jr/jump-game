import time
from typing import Any


def info(*args: Any) -> None:
	# Print the current time
	print(f"[{time.strftime('%H:%M:%S')}]: ", end='')
	print('\033[96m', end='')
	print(*args)
	print('\033[0m', end='')

def error(*args: Any) -> None:
	# Print the current time
	print(f"[{time.strftime('%H:%M:%S')}]: ", end='')
	print('\033[91m', end='')
	print(*args)
	print('\033[0m', end='')

def warn(*args: Any) -> None:
	# Print the current time
	print(f"[{time.strftime('%H:%M:%S')}]: ", end='')
	print('\033[93m', end='')
	print(*args)
	print('\033[0m', end='')