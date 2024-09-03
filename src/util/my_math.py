from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import overload
import math


__all__ = [
	"exponensial_logarithmic_function",
	"Vec2",
	"sign",
	"clamp",
	"EPSILON",
	"fequal",
	"Side",
	"get_side_from_vector",
]


EPSILON = 1e-6


def exponensial_logarithmic_function(value: float) -> float:
	if value < 0:
		return math.exp(value)
	return math.log((value + 1) * value + 1) + 1

def linear_tanh_diff(value: float, asymptote_offset: float, steepness: float = 1.0) -> float:
	return steepness * value - asymptote_offset * math.tanh(value / asymptote_offset)


@dataclass(frozen=True, init=False)
class Vec2:
	x: float
	y: float

	@overload
	def __init__(self, x: float | int, y: float | int) -> None: ...

	@overload
	def __init__(self, x: Vec2) -> None: ...

	@overload
	def __init__(self, x: tuple[float | int, float | int]) -> None: ...
	
	@overload
	def __init__(self, x: float | int) -> None: ...

	def __init__(self, x: float | Vec2 | float | tuple[float, float], y: float | None = None) -> None:
		if isinstance(x, Vec2):
			object.__setattr__(self, "x", x.x)
			object.__setattr__(self, "y", x.y)
		elif isinstance(x, tuple):
			object.__setattr__(self, "x", float(x[0]))
			object.__setattr__(self, "y", float(x[1]))
		elif y is not None:
			object.__setattr__(self, "x", float(x))
			object.__setattr__(self, "y", float(y))
		else:
			object.__setattr__(self, "x", float(x))
			object.__setattr__(self, "y", float(x))

	def __add__(self, other: Vec2) -> Vec2:
		return Vec2(self.x + other.x, self.y + other.y)
	
	def __sub__(self, other: Vec2) -> Vec2:
		return Vec2(self.x - other.x, self.y - other.y)
	
	def __mul__(self, other: float | Vec2) -> Vec2:
		if isinstance(other, Vec2):
			return Vec2(self.x * other.x, self.y * other.y)
		return Vec2(self.x * other, self.y * other)
	
	def __truediv__(self, other: float) -> Vec2:
		return Vec2(self.x / other, self.y / other)

	def __neg__(self) -> Vec2:
		return Vec2(-self.x, -self.y)
	
	def __abs__(self) -> Vec2:
		return Vec2(abs(self.x), abs(self.y))

	def length(self) -> float:
		return (self.x ** 2 + self.y ** 2) ** 0.5
	
	def length2(self) -> float:
		return self.x ** 2 + self.y ** 2

	def normalize(self) -> Vec2:
		length = self.length()
		if length == 0: return Vec2(0, 0)
		return Vec2(self.x / length, self.y / length)
	
	def dot(self, other: Vec2) -> float:
		return self.x * other.x + self.y * other.y
	
	def cross(self, other: Vec2) -> float:
		return self.x * other.y - self.y * other.x
	
	def distance(self, other: Vec2) -> float:
		return (self - other).length()
	
	def distance2(self, other: Vec2) -> float:
		return (self - other).length2()

	def rotate(self, angle: float) -> Vec2:
		cos = math.cos(angle)
		sin = math.sin(angle)
		return Vec2(self.x * cos - self.y * sin, self.x * sin + self.y * cos)

	def to_tuple(self) -> tuple[float, float]:
		return self.x, self.y



@dataclass(frozen=True, init=False)
class IVec2:
	x: int
	y: int

	@overload
	def __init__(self, x: float | int, y: float | int) -> None: ...

	@overload
	def __init__(self, x: IVec2) -> None: ...

	@overload
	def __init__(self, x: tuple[float | int, float | int]) -> None: ...
	
	@overload
	def __init__(self, x: float | int) -> None: ...

	def __init__(self, x: float | IVec2 | float | tuple[float, float], y: float | None = None) -> None:
		if isinstance(x, IVec2):
			object.__setattr__(self, "x", x.x)
			object.__setattr__(self, "y", x.y)
		elif isinstance(x, tuple):
			object.__setattr__(self, "x", int(x[0]))
			object.__setattr__(self, "y", int(x[1]))
		elif y is not None:
			object.__setattr__(self, "x", int(x))
			object.__setattr__(self, "y", int(y))
		else:
			object.__setattr__(self, "x", int(x))
			object.__setattr__(self, "y", int(x))

	def __add__(self, other: IVec2) -> IVec2:
		return IVec2(self.x + other.x, self.y + other.y)
	
	def __sub__(self, other: IVec2) -> IVec2:
		return IVec2(self.x - other.x, self.y - other.y)
	
	def __mul__(self, other: float | IVec2) -> IVec2:
		if isinstance(other, IVec2):
			return IVec2(self.x * other.x, self.y * other.y)
		return IVec2(self.x * other, self.y * other)
	
	def __truediv__(self, other: float) -> Vec2:
		return Vec2(self.x / other, self.y / other)
	
	def __floordiv__(self, other: float) -> IVec2:
		return IVec2(self.x // other, self.y // other)

	def __neg__(self) -> IVec2:
		return IVec2(-self.x, -self.y)
	
	def __abs__(self) -> IVec2:
		return IVec2(abs(self.x), abs(self.y))

	def length(self) -> float:
		return (self.x ** 2 + self.y ** 2) ** 0.5
	
	def length2(self) -> float:
		return self.x ** 2 + self.y ** 2

	def normalize(self) -> IVec2:
		length = self.length()
		if length == 0: return IVec2(0, 0)
		return IVec2(self.x / length, self.y / length)
	
	def dot(self, other: IVec2) -> float:
		return self.x * other.x + self.y * other.y
	
	def cross(self, other: IVec2) -> float:
		return self.x * other.y - self.y * other.x
	
	def distance(self, other: IVec2) -> float:
		return (self - other).length()
	
	def distance2(self, other: IVec2) -> float:
		return (self - other).length2()

	def rotate(self, angle: float) -> IVec2:
		cos = math.cos(angle)
		sin = math.sin(angle)
		return IVec2(self.x * cos - self.y * sin, self.x * sin + self.y * cos)

	def to_tuple(self) -> tuple[float, float]:
		return self.x, self.y

def sign(x: float) -> float:
	if x < 0:
		return -1
	if x > 0:
		return 1
	return 0

def clamp(x: float, min: float, max: float) -> float:
	if x < min:
		return min
	if x > max:
		return max
	return x

def fequal(a: float, b: float) -> bool:
	return abs(a - b) < EPSILON

class Side(Enum):
	LEFT = 0
	RIGHT = 1
	TOP = 2
	BOTTOM = 3


def get_side_from_vector(vec: Vec2) -> Side:
    if abs(vec.x) > abs(vec.y):
        if vec.x > 0:
            return Side.RIGHT
        else:
            return Side.LEFT
    else:
        if vec.y > 0:
            return Side.BOTTOM
        else:
            return Side.TOP

@overload
def ease(value: float, target: float, easing_rate: float, dt: float) -> float: ...

@overload
def ease(value: Vec2, target: Vec2, easing_rate: float, dt: float) -> Vec2: ...

def ease(value: float | Vec2, target: float | Vec2, easing_rate: float, dt: float) -> float | Vec2:
	if isinstance(value, Vec2) and isinstance(target, Vec2):
		return Vec2(
			ease(value.x, target.x, easing_rate, dt),
			ease(value.y, target.y, easing_rate, dt)
		)
	elif isinstance(value, (int, float)) and isinstance(target, (int, float)):
		return target - (target - value) * math.exp(-easing_rate * dt)
	else:
		raise ValueError("Invalid argument types")