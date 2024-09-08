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
_planet_data: list[PlanetData] = []
_player_data = None

_thrust_debug = False
_show_fps = False
_show_bounds = False

_initialized = False

_resolution_changed_callbacks: list[Callable[[int, int], None]] = []

def _init() -> None:
	global _initialized, _available_scenes, _width, _height, _next_scene, _running, _planet_data, _player_data, _thrust_debug
	if _initialized: return
	_initialized = True

	

def _load_player_data() -> PlayerData:
	with open("data/game_data.json", "r") as file:
		game_data: dict[str, Any] = json.load(file)

	global _player_data
	_player_data = PlayerData(
		thrust_up=game_data["player"]["thrust_up"],
		thrust_down=game_data["player"]["thrust_down"],
		thrust_decay=game_data["player"]["thrust_decay"]
	)

	return _player_data

def _load_planet_data() -> None:
	with open("data/game_data.json", "r") as file:
		game_data: dict[str, Any] = json.load(file)

	global _planet_data

	for id, planet in enumerate(game_data["planets"]):
		name = planet["name"]
		_planet_data.append(PlanetData(
			id=id,
			name=name,
			gravity=planet["gravity"],
			drag=planet["drag"],
			game_speed=planet["game_speed"],
			game_acceleration=planet["game_acceleration"],
			sprite_path=f"assets/image/planets/{name}.png",
			translation_key=f"planet.{name}.name"
		))

		levels: list[LevelData] = []
		level_files = []
		try:
			level_files = sorted(os.listdir(f"data/levels/{name}/"))
		except FileNotFoundError:
			log.warn(f"No levels found for planet {name}")
		finally:
			for level_id, file in enumerate(level_files):
				if file.endswith(".txt"):
					raw_level_data = None

					with open(f"data/levels/{name}/{file}", "r") as f:
						raw_level_data = f.read()
					
					if level_id != int(file[:-4]):
						log.warn(f"Level ID mismatch in {file}")

					level_data = _parse_level_data(raw_level_data)

					levels.append(LevelData(
						id=level_id,
						planet_id=id,
						level_data=level_data,
						width=len(level_data[0]),
						height=len(level_data)
					))
			
			_planet_data[id].levels = tuple(levels)

def _parse_level_data(raw_level_data: str) -> list[list[str]]:
	level_data: list[list[str]] = []

	width = len(max(raw_level_data.splitlines(), key=len))
	for row in raw_level_data.splitlines():
		level_data.append(list(row.ljust(width, " ")))

	return level_data

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

def get_player_data() -> PlayerData:
	global _player_data
	if _player_data is None:
		return _load_player_data()
	
	return _player_data

def get_planet_data(id: int) -> PlanetData:
	if not _planet_data:
		_load_planet_data()
	return _planet_data[id]

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