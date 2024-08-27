from __future__ import annotations
from core import IScene, app_state, PlanetData, Level
import pygame
from gui import Container, LabelElement, Style
from styles import LABEL_STYLE
import util.language_manager as lm
from enum import Enum
from dataclasses import dataclass
from typing import Optional
from abc import ABC, abstractmethod
import util.logger as log
import math


GRAVITY_BASE = 20
INPUT_IMPULSE_JUMP = 800
INPUT_IMPULSE_UP = 100
INPUT_IMPULSE_DOWN = 50
INPUT_DECAY_SPEED = 1.0


def _aabb(a: IHasAABB, b: IHasAABB) -> bool:
	# Unpack the coordinates of the two AABBs
	a_left, a_top, a_right, a_bottom = a.get_aabb()
	b_left, b_top, b_right, b_bottom = b.get_aabb()
	
	return a_left < b_right and a_right > b_left and a_top < b_bottom and a_bottom > b_top

def _sided_aabb(player: IHasAABB, obstacle: IHasAABB) -> Side:
	if not _aabb(player, obstacle): return Side.NONE

	TOLERANCE = 0.1

	# Unpack the player and obstacle coordinates
	p_left, p_top, p_right, p_bottom = player.get_aabb()
	o_left, o_top, o_right, o_bottom = obstacle.get_aabb()
	
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

class IHasAABB(ABC):
	@abstractmethod
	def get_aabb(self) -> tuple[float, float, float, float]: ...

class Camera(IHasAABB):
	def __init__(self, zoom: float = 1.0) -> None:
		self._x = 0
		self._y = 0
		self._zoom = zoom

	@property
	def x(self) -> float:
		return self._x
	
	@property
	def y(self) -> float:
		return self._y
	
	def zoom(self, delta: float) -> None:
		self._zoom += delta
		if self._zoom < 0.1:
			self._zoom = 0.1
		log.info(f"Zoom: {self._zoom}")

	def follow_player(self, player: Player, level: Level) -> None:
		RELATIVE_X = 0.2
		RELATIVE_Y = 0.2
		view_width = app_state.width / self._zoom
		view_height = app_state.height / self._zoom
		self._x = player.x - view_width * RELATIVE_X + player.width / 2
		self._y = player.y - view_height * RELATIVE_Y + player.height / 2

		# Clamp the camera to the level bounds
		if self._x < 0:
			self._x = 0
		if self._y < 0:
			self._y = 0
		if self._x + view_width > level.width:
			self._x = level.width - view_width
		if self._y + view_height > level.height:
			self._y = level.height - view_height
	
	def apply(self, x: float, y: float, width: float, height: float) -> tuple[int, int, int, int]:
		new_x = math.floor((x - self._x) * self._zoom)
		new_y = math.floor((y - self._y) * self._zoom)
		new_w = math.ceil(width * self._zoom)
		new_h = math.ceil(height * self._zoom)
		return int(new_x), int(new_y), int(new_w), int(new_h)
	
	def get_aabb(self) -> tuple[float, float, float, float]:
		return self._x, self._y, self._x + app_state.width / self._zoom, self._y + app_state.height / self._zoom

	def clip(self, entity: IHasAABB) -> bool:
		return not _aabb(self, entity)
	
class Tile(IHasAABB):
	def __init__(self, x: float, y: float, width: float = 1, height: float = 1) -> None:
		self.x = x
		self.y = y
		self.width = width
		self.height = height

	def get_aabb(self) -> tuple[float, float, float, float]:
		"""Get the axis-aligned bounding box of the tile. The format is (left, top, right, bottom)."""
		return self.x, self.y, self.x + self.width, self.y + self.height

	def get_x(self) -> float:
		return self.x

	def get_y(self) -> float:
		return self.y
	
	def get_width(self) -> float:
		return self.width
	
	def get_height(self) -> float:
		return self.height

	def render(self, screen: pygame.Surface, camera: Camera) -> None:
		if camera.clip(self): return
		rect = camera.apply(self.x, self.y, self.width, self.height)
		pygame.draw.rect(screen, (255, 255, 255), rect)

class Player(IHasAABB):
	def __init__(self) -> None:
		self.x: float = 0
		self.y: float = 0
		self.vel_x: float = 0
		self.vel_y: float = 0
		self.impulse_x: float = 0
		self.impulse_y: float = 0
		self.width: float = 0.3
		self.height: float = 0.3
		self.on_ground: bool = True
		self.on_ceiling: bool = False

	def set_position(self, x: float, y: float) -> None:
		self.x = x
		self.y = y

	def apply_impulse_y(self, y: float, dt: float) -> None:
		self.vel_y += y * dt
	
	def set_velocity_x(self, x: float) -> None:
		self.vel_x = x
	
	def apply_gravity_y(self, gravity: float, dt: float) -> None:
		self.vel_y += gravity * GRAVITY_BASE * dt
	
	def apply_drag_y(self, drag: float, dt: float) -> None:
		self.vel_y -= self.vel_y * drag * dt

	def integrate(self, dt: float) -> None:
		self.x += self.vel_x * dt
		self.y += self.vel_y * dt

	def handle_input(self, dt: float) -> None:
		key_state = pygame.key.get_pressed()

		print(math.exp(-self.vel_y * INPUT_DECAY_SPEED))
		if key_state[pygame.K_UP] or key_state[pygame.K_SPACE]:
			if self.on_ground:
				self.apply_impulse_y(-INPUT_IMPULSE_JUMP, dt)
			else:
				self.apply_impulse_y(-INPUT_IMPULSE_UP, dt)
		if key_state[pygame.K_DOWN] or key_state[pygame.K_LSHIFT]:
			self.apply_impulse_y(INPUT_IMPULSE_DOWN, dt)

	def stop_y_movement(self, new_y: float) -> None:
		self.vel_y = 0
		self.y = new_y

	def update(self, dt: float, planet: PlanetData) -> None:
		self.handle_input(dt)
		self.apply_gravity_y(planet.gravity, dt)
		self.apply_drag_y(planet.drag, dt)
		self.integrate(dt)
	
	def get_aabb(self) -> tuple[float, float, float, float]:
		"""Get the axis-aligned bounding box of the player. The format is (left, top, right, bottom)."""
		return self.x, self.y, self.x + self.width, self.y + self.height

	def render(self, screen: pygame.Surface, camera: Camera) -> None:
		if camera.clip(self): return
		rect = camera.apply(self.x, self.y, self.width, self.height)
		pygame.draw.ellipse(screen, (255, 0, 0), rect)

class Side(Enum):
    NONE = 0
    TOP = 1
    BOTTOM = 2
    LEFT = 3
    RIGHT = 4

class LevelScene(IScene):
	def __init__(self, planet: PlanetData) -> None:
		self.planet = planet
		
		pygame.display.set_caption(lm.get("caption.driving_on").format(lm.get(self.planet.translation_key)))

		self.gui = Container().with_children(
			LabelElement(lm.get(planet.translation_key), style=LABEL_STYLE),
		)
		
		if planet.current_level >= len(planet.levels):
			raise ValueError("Invalid level ID")
		self.level = planet.levels[planet.current_level]
		self.load_level()

		self.camera = Camera(65)

		self.player = Player()
		self.player.set_position(0.5 - self.player.width / 2, self.calc_start_y() - self.player.height)
		self.player.set_velocity_x(self.planet.game_speed)

	def calc_start_y(self) -> float:
		for y in range(self.level.height):
			if y == 0 or self.level.level_data[y-1][0] == "#":
				continue
			if self.level.level_data[y][0] == "#":
				return y

	def add_tile(self, x, y) -> None:
		if y == 0:
			self.tiles.append(Tile(x, y - 31, 1, 32)) # you can't fly over that
		else:
			self.tiles.append(Tile(x, y))

	def load_level(self) -> None:
		# TODO: possibly joid inner tiles into more bigger ones, this could optimize the collision detection and rendering
		self.tiles: list[Tile] = []
		for y in range(self.level.height):
			for x in range(self.level.width):
				if self.level.level_data[y][x] == "#":
					self.add_tile(x, y)
					

	def handle_event(self, event: pygame.event.Event) -> None: ...
	
	def kill(self) -> None:
		app_state.queue_scene("game_over", self.planet)

	def collide(self) -> None:
		if self.player.y > self.level.height:
			self.kill()

		for tile in self.tiles:
			side = _sided_aabb(self.player, tile)
			if side == Side.TOP:
				self.player.stop_y_movement(tile.get_y() + tile.get_height())
				self.player.on_ground = True
			else:
				self.player.on_ground = False
			if side == Side.BOTTOM:
				self.player.stop_y_movement(tile.get_y() - self.player.height)
				self.player.on_ceiling = True
			else:
				self.player.on_ceiling = False
			
			if side == Side.LEFT or side == Side.RIGHT:
				self.kill()

	def update(self, dt: float) -> None:
		self.player.update(dt, self.planet)
		self.collide()
		self.gui.update(dt)
		self.camera.follow_player(self.player, self.level)

	def render(self, screen: pygame.Surface) -> None:
		screen.fill((0, 0, 0))

		for tile in self.tiles:
			tile.render(screen, self.camera)

		self.player.render(screen, self.camera)

		#self.gui.render(screen)

		pygame.display.flip()
	
	@classmethod
	def get_name(cls) -> str:
		return "level"
