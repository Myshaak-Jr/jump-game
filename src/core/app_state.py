from .scene import IScene
from typing import Type
import json
from typing import Any


class AppState:
	def __init__(self) -> None:
		self._available_scenes = {}
		self._width = 0
		self._height = 0
		self._next_scene: IScene = None
		self._running = False
		with open("assets/data/planet_data.json", "r") as file:
			self._planet_data: dict[str, dict[str, Any]] = json.load(file)

	def set_window_size(self, width: int, height: int) -> None:
		self._width = width
		self._height = height

	@property
	def width(self) -> int:
		return self._width
	
	@width.setter
	def width(self, value: int) -> None:
		self._width = value
		
	@property
	def height(self) -> int:
		return self._height

	@height.setter
	def height(self, value: int) -> None:
		self._height = value

	def register_scene(self, scene: Type[IScene]) -> None:
		self._available_scenes[scene.name] = scene

	def queue_scene(self, scene: str | IScene, *args, **kwargs) -> None:
		if isinstance(scene, IScene):
			self._next_scene = scene
		else:
			self._next_scene = self._available_scenes[scene](*args, **kwargs)

	def queue_stop(self) -> None:
		self._running = False
	
	def get_planet_data(self, planet: str) -> dict[str, Any]:
		return self._planet_data[planet]


app_state = AppState()