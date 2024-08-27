from .scene import IScene
from typing import Type
import json
from typing import Any
from dataclasses import dataclass
import os
import util.logger as log


@dataclass
class Level:
	id: int
	planet_id: int
	level_data: list[list[str]]
	width: int
	height: int

@dataclass
class PlanetData:
	id : int
	name: str
	gravity: float
	drag: float
	game_speed: float
	sprite_path: str
	translation_key: str
	levels: tuple[Level] = ()
	current_level: int = None

class AppState:
	def __init__(self) -> None:
		self._available_scenes = {}
		self._width = 0
		self._height = 0
		self._next_scene: IScene = None
		self._running = False
		self._planet_data: list[PlanetData] = []
		
		with open("data/planet_data.json", "r") as file:
			planets_json = json.load(file)["planets"]

		for id, planet in enumerate(planets_json):
			name = planet["name"]

			self._planet_data.append(PlanetData(
				id=id,
				name=name,
				gravity=planet["gravity"],
				drag=planet["drag"],
				game_speed=planet["game_speed"],
				sprite_path=f"assets/image/planets/{name}.png",
				translation_key=f"planet.{name}.name"
			))

			levels: list[Level] = []
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

						level_data = self._parse_level_data(raw_level_data)

						levels.append(Level(
							id=level_id,
							planet_id=id,
							level_data=level_data,
							width=len(level_data[0]),
							height=len(level_data)
						))
				self._planet_data[id].levels = tuple(levels)

	def _parse_level_data(self, raw_level_data: str) -> list[list[str]]:
		level_data = []

		width = len(max(raw_level_data.splitlines(), key=len))
		for row in raw_level_data.splitlines():
			level_data.append(list(row.ljust(width, " ")))

		return level_data
		
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
		if scene.get_name() in self._available_scenes:
			log.warn(f"Scene {scene.get_name()} already registered")
			return
		self._available_scenes[scene.get_name()] = scene
		log.info(f"Registed scene {scene.get_name()}")

	def queue_scene(self, scene: str | IScene, *args, **kwargs) -> None:
		if isinstance(scene, IScene):
			self._next_scene = scene
		else:
			log.info(f"Creating new scene {scene}")
			if scene not in self._available_scenes:
				raise ValueError(f"Attemped to queue unknown scene {scene}")
			self._next_scene = self._available_scenes[scene](*args, **kwargs)

	def queue_stop(self) -> None:
		self._running = False
	
	def get_planet_data(self, id: int) -> PlanetData:
		return self._planet_data[id]


app_state = AppState()