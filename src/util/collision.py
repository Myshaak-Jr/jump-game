# https://noonat.github.io/intersect/
from dataclasses import dataclass
from typing import Optional
from pygame.math import Vector2


@dataclass
class Hit:
	pos: Vector2
	delta: Vector2
	normal: Vector2
	time: float

@dataclass
class Sweep:
	hit: Optional[Hit]
	pos: Vector2
	time: float = 1.0

@dataclass
class AABB:
	center: Vector2
	half_size: Vector2


