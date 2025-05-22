import json
import os
import util.logger as log
from typing import Any
from .structs import PlanetData, LevelData, PlayerData

__all__ = [
	"get_level",
	"get_planet",
	"get_player_data",
	"get_planet_data",
	"get_last_level",
	"set_last_level",
	"get_next_level",
	"get_next_planet",
	"load_last_level",
	"save_last_level"
]

_planet_data: list[PlanetData] = []
_level_data: list[LevelData] = []
_player_data = None | PlayerData

_last_level: LevelData | None = None

SAVE_FILE = "data/save_file.json"


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

def _load_level_data() -> None:
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

		level_files = []
		try:
			level_files = sorted(os.listdir(f"data/levels/{name}/"))
		except FileNotFoundError:
			log.warn(f"No levels found for planet {name}")
		finally:
			_planet_data[id].num_levels = len(level_files)
			for level_id, file in enumerate(level_files):
				if file.endswith(".txt"):
					raw_level_data = None

					with open(f"data/levels/{name}/{file}", "r") as f:
						raw_level_data = f.read()
					
					if level_id != int(file[:-4]):
						log.warn(f"Level ID mismatch in {file}")

					level_data = _parse_level_data(raw_level_data)

					_level_data.append(LevelData(
						id=level_id,
						planet=_planet_data[id],
						level_data=level_data,
						width=len(level_data[0]),
						height=len(level_data)
					))

def _parse_level_data(raw_level_data: str) -> list[list[str]]:
	level_data: list[list[str]] = []

	width = len(max(raw_level_data.splitlines(), key=len))
	for row in raw_level_data.splitlines():
		level_data.append(list(row.ljust(width, " ")))

	return level_data

def get_level(planet: str, id: int) -> LevelData | None:
	if not _level_data:
		_load_level_data()

	for level in _level_data:
		if level.planet.name == planet and level.id == id:
			return level
	
	return None
	
def get_planet(planet: str) -> PlanetData | None:
	if not _planet_data:
		_load_level_data()

	for planet_data in _planet_data:
		if planet_data.name == planet:
			return planet

	return None

def load_last_level() -> None:
	with open(SAVE_FILE, "r") as file:
		save_data = json.load(file)
	
	level = get_level(save_data["last_planet_name"], save_data["last_level_id"])
	if level is None:
		log.warn("Could not load last level")
		return
	
	set_last_level(level)

def save_last_level() -> None:
	if _last_level is None:
		log.warn("No last level to save")
		return
	
	with open(SAVE_FILE, "w") as file:
		json.dump({
			"last_planet_name": _last_level.planet.name,
			"last_level_id": _last_level.id
		}, file)

def get_last_level() -> LevelData | None:
	return _last_level

def set_last_level(level: LevelData) -> None:
	global _last_level
	_last_level = level

def get_next_level() -> LevelData | None:
	if _last_level is None:
		return None
	
	next_level_id = _last_level.id + 1
	next_planet = _last_level.planet
	if next_level_id >= _last_level.planet.num_levels:
		next_planet = get_next_planet(_last_level.planet)
		return None
	
	return get_level(next_planet.name, next_level_id)
	
def get_next_planet(planet: PlanetData) -> PlanetData | None:
	planet_id = planet.id + 1
	if planet_id >= len(_planet_data):
		return None
	
	return _planet_data[planet_id]

def get_player_data() -> PlayerData:
	global _player_data
	if _player_data is None:
		return _load_player_data()
	
	return _player_data

def get_planet_data(id: int) -> PlanetData:
	if not _planet_data:
		_load_level_data()
	return _planet_data[id]
