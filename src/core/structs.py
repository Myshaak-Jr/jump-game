from dataclasses import dataclass
from typing import Any


__all__ = [
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
	game_acceleration: float
	sprite_path: str
	translation_key: str
	levels: tuple[LevelData, ...] = ()
	current_level: int = 0

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

