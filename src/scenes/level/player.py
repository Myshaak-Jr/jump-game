from typing import overload
import pygame
from .camera import Camera
from .collision import IHasAABB
from core import PlanetData, PlayerData
from pygame.math import Vector2
import math


class Player(IHasAABB):
	def __init__(self, player_data: PlayerData, planet_data: PlanetData) -> None:
		self._player_data = player_data
		self._planet_data = planet_data

		self._pos = Vector2(0)
		self._vel = Vector2(0)
		self._impulse = Vector2(0)

		self._size = Vector2(0.3, 0.3)

		self.on_ground: bool = False

	@overload
	def set_position(self, x: float, y: float) -> None: ...

	@overload
	def set_position(self, x: Vector2) -> None: ...

	def set_position(self, x: float | Vector2, y: float | None = None) -> None:
		if isinstance(x, Vector2):
			self._pos = x
		else:
			self._pos = Vector2(x)
	
	@overload
	def set_velocity(self, x: float, y: float) -> None: ...

	@overload
	def set_velocity(self, x: Vector2) -> None: ...

	def set_velocity(self, x: float | Vector2, y: float | None = None) -> None:
		if isinstance(x, Vector2):
			self._vel = x
		else:
			self._vel = Vector2(x)

	@overload
	def apply_impulse(self, x: float, y: float) -> None: ...

	@overload
	def apply_impulse(self, x: Vector2) -> None: ...

	def apply_impulse(self, x: Vector2 | float, y: float | None = None) -> None:
		if isinstance(x, Vector2):
			self._impulse += x
		else:
			self._impulse += Vector2(x)
	
	def _apply_gravity(self) -> None:
		self.apply_impulse(Vector2(0, self._planet_data.gravity))
	
	def _apply_drag(self) -> None:
		self.apply_impulse(0, -self._vel.x * self._planet_data.drag)

	def _integrate(self, dt: float) -> None:
		self._vel += self._impulse * dt
		self._pos += self._vel * dt

		self._impulse = Vector2(0)

	@staticmethod
	def _calc_thrust_power(x: float, decay: float) -> float:
		# https://www.geogebra.org/calculator/vtr4t243
		if x > 0.0:
			return math.exp(-x * decay)
		else:
			a = x * decay
			return math.log(a**2 - a + 1) + 1

	def _calc_up_impulse(self) -> Vector2:
		y = -self._player_data.thrust * self._calc_thrust_power(-self._vel.y, self._player_data.thrust_decay)
		return Vector2(0, y)
	
	def _calc_down_impulse(self) -> Vector2:
		y = self._player_data.thrust * self._calc_thrust_power(self._vel.y, self._player_data.thrust_decay)
		return Vector2(0, y)

	def _handle_input(self) -> None:
		key_state = pygame.key.get_pressed()
		if key_state[pygame.K_UP] or key_state[pygame.K_SPACE]:
			self.apply_impulse(self._calc_up_impulse())
		if key_state[pygame.K_DOWN] or key_state[pygame.K_LSHIFT]:
			self.apply_impulse(self._calc_down_impulse())

	def stop_y_movement(self, new_y: float) -> None:
		self._vel.y = 0
		self._pos.y = new_y

	def update(self, dt: float) -> None:
		self._handle_input()
		self._apply_gravity()
		self._apply_drag()
		self._integrate(dt)
	
	def get_x(self) -> float:
		return self._pos.x

	def get_y(self) -> float:
		return self._pos.y
	
	def get_width(self) -> float:
		return self._size.x
	
	def get_height(self) -> float:
		return self._size.y

	def render(self, screen: pygame.Surface, camera: Camera) -> None:
		if camera.clip(self): return
		rect = camera.apply(self)
		if self.on_ground:
			pygame.draw.rect(screen, (0, 255, 0), rect)
		else:
			pygame.draw.ellipse(screen, (255, 0, 0), rect)