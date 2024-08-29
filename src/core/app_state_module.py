from .scene import IScene
from typing import Type, Any, overload
import json
from dataclasses import dataclass
import os
import util.logger as log


__all__ = [
	"AppState",
	"app_state",
	"PlanetData",
	"LevelData",
	"PlayerData",
	"NewSceneData"
]


@dataclass
class LevelData:
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
	levels: tuple[LevelData, ...] = ()
	current_level: int = 0

@dataclass
class PlayerData:
	thrust: float
	thrust_decay: float


@dataclass
class NewSceneData:
	name: str
	args: tuple[Any, ...]
	kwargs: dict[Any, Any]

class AppState:
	def __init__(self) -> None:
		self._available_scenes: dict[str, type[IScene]] = {}
		self._width = 0
		self._height = 0
		self._next_scene: NewSceneData | IScene | None = None
		self._running = False
		self._planet_data: list[PlanetData] = []
		self._player_data = None
		self._debug = False
		
		with open("data/game_data.json", "r") as file:
			game_data: dict[str, Any] = json.load(file)

		self._load_planet_data(game_data)
		self._load_player_data(game_data)

	def _load_player_data(self, game_data: dict[str, Any]) -> None:
		self._player_data = PlayerData(
			thrust=game_data["player"]["thrust"],
			thrust_decay=game_data["player"]["thrust_decay"]
		)

	def _load_planet_data(self, game_data: dict[str, Any]) -> None:
		for id, planet in enumerate(game_data["planets"]):
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

						level_data = self._parse_level_data(raw_level_data)

						levels.append(LevelData(
							id=level_id,
							planet_id=id,
							level_data=level_data,
							width=len(level_data[0]),
							height=len(level_data)
						))
				
				self._planet_data[id].levels = tuple(levels)

	def _parse_level_data(self, raw_level_data: str) -> list[list[str]]:
		level_data: list[list[str]] = []

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

	def get_scene(self, name: str) -> Type[IScene]:
		if name not in self._available_scenes:
			raise ValueError(f"Scene {name} not registered")
		return self._available_scenes[name]

	def register_scene(self, scene: Type[IScene]) -> None:
		if scene.get_name() in self._available_scenes:
			log.warn(f"Scene {scene.get_name()} already registered")
			return
		self._available_scenes[scene.get_name()] = scene
		log.info(f"Registed scene {scene.get_name()}")

	@overload
	def queue_scene(self, scene: IScene) -> None: ...

	@overload
	def queue_scene(self, scene: str, *args: Any, **kwargs: Any) -> None: ...

	@overload
	def queue_scene(self, scene: NewSceneData) -> None: ...

	def queue_scene(self, scene: str | IScene | NewSceneData, *args: Any, **kwargs: Any) -> None:
		if isinstance(scene, str):
			self._next_scene = NewSceneData(scene, args, kwargs)
		else:
			self._next_scene = scene

	def has_scene(self, name: str) -> bool:
		print(self._available_scenes, name)
		a = name in self._available_scenes
		print(a)
		return a
	
	def get_next_scene(self) -> NewSceneData | IScene | None:
		return self._next_scene
	
	def clear_next_scene(self) -> None:
		self._next_scene = None

	def is_running(self) -> bool:
		return self._running
	
	def start(self) -> None:
		self._running = True

	def queue_stop(self) -> None:
		self._running = False

	def get_player_data(self) -> PlayerData:
		if not self._player_data:
			raise ValueError("Player data not loaded")
		return self._player_data
	
	def get_planet_data(self, id: int) -> PlanetData:
		return self._planet_data[id]


app_state = AppState()
