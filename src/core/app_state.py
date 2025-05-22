from collections.abc import Callable
from .scene import IScene
from typing import Type, Any, overload
from .structs import PlanetData, LevelData, PlayerData, NewSceneData
import json
import os
import util.logger as log


__all__ = [
	"set_window_size",
	"get_width",
	"set_width",
	"get_height",
	"set_height",
	"get_scene",
	"register_scene",
	"queue_scene",
	"has_scene",
	"get_next_scene",
	"clear_next_scene",
	"is_running",
	"start",
	"queue_stop",
	"get_player_data",
	"get_planet_data",
	"enable_thrust_debug",
	"is_thrust_debug",
]


_available_scenes: dict[str, type[IScene]] = {}
_width = 0
_height = 0
_next_scene: NewSceneData | IScene | None = None
_running = False

_thrust_debug = False
_show_fps = False
_show_bounds = False

_initialized = False

_resolution_changed_callbacks: list[Callable[[int, int], None]] = []

def _init() -> None:
	global _initialized, _available_scenes, _width, _height, _next_scene, _running, _thrust_debug
	if _initialized: return
	_initialized = True

def register_resolution_changed_callback(callback: Callable[[int, int], None]) -> None:
	_resolution_changed_callbacks.append(callback)

@overload
def set_window_size(size_or_width: int, height: int) -> None: ...

@overload
def set_window_size(size_or_width: tuple[int, int]) -> None: ...

def set_window_size(size_or_width: int | tuple[int, int], height: int | None = None) -> None:
	if isinstance(size_or_width, tuple):
		width, height = size_or_width
	else:
		width = size_or_width
		if height is None:
			raise ValueError("Invalid window size")

	global _width, _height
	_width = width
	_height = height

	for callback in _resolution_changed_callbacks:
		callback(width, height)

def get_window_size() -> tuple[int, int]:
	return _width, _height

def get_width() -> int:
	return _width

def set_width(value: int) -> None:
	global _width
	_width = value
	
def get_height() -> int:
	return _height

def set_height(value: int) -> None:
	global _height
	_height = value

def get_scene(name: str) -> Type[IScene]:
	if name not in _available_scenes:
		raise ValueError(f"Scene {name} not registered")
	return _available_scenes[name]

def register_scene(scene: Type[IScene]) -> None:
	global _available_scenes
	if scene.get_name() in _available_scenes:
		log.warn(f"Scene {scene.get_name()} already registered")
		return
	_available_scenes[scene.get_name()] = scene
	log.info(f"Registed scene {scene.get_name()}")

@overload
def queue_scene(scene: IScene) -> None: ...

@overload
def queue_scene(scene: str, *args: Any, **kwargs: Any) -> None: ...

@overload
def queue_scene(scene: NewSceneData) -> None: ...

def queue_scene(scene: str | IScene | NewSceneData, *args: Any, **kwargs: Any) -> None:
	global _next_scene
	if isinstance(scene, str):
		_next_scene = NewSceneData(scene, args, kwargs)
	else:
		_next_scene = scene

def has_scene(name: str) -> bool:
	return name in _available_scenes

def get_next_scene() -> NewSceneData | IScene | None:
	return _next_scene

def clear_next_scene() -> None:
	global _next_scene
	_next_scene = None

def is_running() -> bool:
	return _running

def start() -> None:
	global _running
	_running = True

def queue_stop() -> None:
	global _running
	_running = False

def enable_thrust_debug() -> None:
	global _thrust_debug
	_thrust_debug = True

def is_thrust_debug() -> bool:
	return _thrust_debug

def enable_fps() -> None:
	global _show_fps
	_show_fps = True

def show_fps() -> bool:
	return _show_fps

def enable_bounds() -> None:
	global _show_bounds
	_show_bounds = True

def disable_bounds() -> None:
	global _show_bounds
	_show_bounds = False

def toggle_bounds() -> None:
	global _show_bounds
	_show_bounds = not _show_bounds

def show_bounds() -> bool:
	return _show_bounds

# initialize the app state
_init()