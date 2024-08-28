# https://noonat.github.io/intersect/
from dataclasses import dataclass
from pygame.math import Vector2
import pygame
from abc import ABC, abstractmethod
from enum import Enum


@dataclass
class Hit:
	pos: Vector2
	delta: Vector2
	normal: Vector2
	time: float

@dataclass
class Sweep:
	hit: Hit | None
	pos: Vector2
	time: float = 1.0

@dataclass
class AABB:
	"""Axis-aligned bounding box."""
	center: Vector2
	half_size: Vector2


class IHasAABB(ABC):
	@abstractmethod
	def get_x(self) -> float: ...

	@abstractmethod
	def get_y(self) -> float: ...

	@abstractmethod
	def get_width(self) -> float: ...

	@abstractmethod
	def get_height(self) -> float: ...

	def get_size(self) -> Vector2:
		return Vector2(self.get_width(), self.get_height())

	def get_pos(self) -> Vector2:
		return Vector2(self.get_x(), self.get_y())

	def get_aabb(self) -> AABB:
		half_size = Vector2(self.get_width() / 2, self.get_height() / 2)
		return AABB(Vector2(self.get_x(), self.get_y()) + half_size, half_size)
	
	def get_rect(self) -> pygame.FRect:
		return pygame.FRect(self.get_x(), self.get_y(), self.get_width(), self.get_height())
	

def aabb(a: IHasAABB, b: IHasAABB) -> bool:
	a_aabb = a.get_aabb()
	b_aabb = b.get_aabb()

	a_min = a_aabb.center - a_aabb.half_size
	a_max = a_aabb.center + a_aabb.half_size
	b_min = b_aabb.center - b_aabb.half_size
	b_max = b_aabb.center + b_aabb.half_size

	return a_min.x < b_max.x and a_max.x > b_min.x and a_min.y < b_max.y and a_max.y > b_min.y


class Side(Enum):
	TOP = 0
	BOTTOM = 1
	LEFT = 2
	RIGHT = 3
	NONE = 4

def sided_aabb(player: IHasAABB, obstacle: IHasAABB) -> Side:
	if not aabb(player, obstacle): return Side.NONE

	# TODO: add sweeping

	TOLERANCE = 0.2

	# Unpack the player and obstacle coordinates
	a_aabb = player.get_aabb()
	b_aabb = obstacle.get_aabb()

	a_min = a_aabb.center - a_aabb.half_size
	a_max = a_aabb.center + a_aabb.half_size
	b_min = b_aabb.center - b_aabb.half_size
	b_max = b_aabb.center + b_aabb.half_size

	p_left, p_top = a_min
	p_right, p_bottom = a_max
	o_left, o_top = b_min
	o_right, o_bottom = b_max
	
	# Calculate the half-widths and half-heights
	p_half_width = (p_right - p_left) / 2
	p_half_height = (p_bottom - p_top) / 2
	o_half_width = (o_right - o_left) / 2
	o_half_height = (o_bottom - o_top) / 2
	
	# Calculate the centers of the player and the obstacle
	p_center_x = p_left + p_half_width
	p_center_y = p_top + p_half_height
	o_center_x = o_left + o_half_width
	o_center_y = o_top + o_half_height
	
	# Calculate the difference between the centers
	dx = p_center_x - o_center_x
	dy = p_center_y - o_center_y
	
	# Calculate the minimum distances to separate along X and Y axes
	combined_half_width = p_half_width + o_half_width
	combined_half_height = p_half_height + o_half_height
	
	# Determine the collision side based on the minimum overlap
	overlap_x = combined_half_width - abs(dx)
	overlap_y = combined_half_height - abs(dy)
	
	if overlap_x + TOLERANCE < overlap_y:
		# Collision on the left or right
		if dx > 0:
			return Side.LEFT
		else:
			return Side.RIGHT
	else:
		# Collision on the top or bottom
		if dy > 0:
			return Side.BOTTOM
		else:
			return Side.TOP