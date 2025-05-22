from dataclasses import dataclass
from typing import Any


__all__ = [
	"PlanetData",
	"LevelData",
	"PlayerData",
	"NewSceneData"
]


@dataclass
class PlanetData:
	id : int
	name: str
	gravity: float
	drag: float
	game_speed: float
	game_acceleration: float
	sprite_path: str
	translation_key: str
	num_levels: int = 0

@dataclass
class LevelData:
	id: int
	level_data: list[list[str]]
	width: int
	height: int
	planet: PlanetData

@dataclass
class PlayerData:
	thrust_up: float
	thrust_down: float
	thrust_decay: float

@dataclass
class NewSceneData:
	name: str
	args: tuple[Any, ...]
	kwargs: dict[Any, Any]

