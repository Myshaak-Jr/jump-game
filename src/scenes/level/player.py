from typing import override
import pygame
import pymunk
import pymunk.space
from .util import IHasRect
from util.my_math import Vec2
from .camera import Camera
from core import PlanetData, PlayerData
import math
from .util import GLOBAL_SCALE


__all__ = [
	"Player",
]


class Player(IHasRect):
	def __init__(self, space: pymunk.Space, x: float, y: float, width: float, planet: PlanetData, player_data: PlayerData):
		self._planet = planet
		self._player_data = player_data
		self._color = (255, 0, 0)
		self._alive = True

		# Pygame representation
		self._rect = pygame.FRect(x, y, width, width)
		
		# Pymunk representation
		self._body = pymunk.Body(1, 1)  # Mass and moment of inertia
		self._body.position = (x + width / 2, y + width / 2)
		self._shape = pymunk.Circle(self._body, width / 2)
		self._shape.density = 1
		self._shape.elasticity = 0.5
		self._shape.friction = 0.5

		# Collision type to identify player
		self._shape.collision_type = 1
		
		# Add the shape to the space
		space.add(self._body, self._shape)

		# Apply a force to the right
		self._push_right()
	
	def render(self, screen: pygame.Surface, camera: Camera):
		if camera.clip(self): return
		rect = camera.apply(self)

		pygame.draw.circle(screen, self._color, (int(rect.x + rect.width / 2), int(rect.y + rect.width / 2)), int(rect.width / 2), 1)

		pygame.draw.circle(screen, self._color, (int(rect.x + rect.width / 2), int(rect.y + rect.width / 2)), 2)

		angle = self._body.angle
		pygame.draw.line(screen, self._color, (rect.x + rect.width / 2, rect.y + rect.width / 2), (rect.x + rect.width / 2 + math.cos(angle) * rect.width / 2, rect.y + rect.width / 2 + math.sin(angle) * rect.width / 2), 1)
		
	
	def set_pos(self, pos: Vec2):
		self._body.position = (pos.x + self._rect.width / 2, pos.y + self._rect.width / 2)

		self._rect.x = self._body.position.x - self._rect.width / 2 # type: ignore
		self._rect.y = self._body.position.y - self._rect.width / 2 # type: ignore

	@override
	def get_rect(self) -> pygame.FRect:
		return self._rect

	def update(self, level_size: Vec2):
		# Update the position based on Pymunk simulation
		self._rect.x = self._body.position.x - self._rect.width / 2
		self._rect.y = self._body.position.y - self._rect.width / 2

		if self._body.velocity.x <= 0.0:
			self._alive = False
		if self._rect.y > level_size.y:
			self._alive = False
	
	def physics_update(self):
		if not self._alive: return
		if self._body.velocity.x < self._planet.game_speed * GLOBAL_SCALE:
			self._push_right()

		key_state = pygame.key.get_pressed()
		if key_state[pygame.K_SPACE]:
			force = Vec2(0, -self._calc_thrust_power(1))
			force = force.rotate(-self._body.angle)
			self._body.apply_force_at_local_point(force.to_tuple())
		if key_state[pygame.K_LSHIFT]:
			force = Vec2(0, self._calc_thrust_power(-1))
			force = force.rotate(-self._body.angle)
			self._body.apply_force_at_local_point(force.to_tuple())

	def _push_right(self):
		force = Vec2(10, 0)
		force = force.rotate(-self._body.angle)
		self._body.apply_impulse_at_local_point(force.to_tuple())

		#self._body.velocity = self._planet.game_speed * GLOBAL_SCALE, self._body.velocity.y
	
	def is_alive(self) -> bool:
		return self._alive
			
	def get_width(self) -> float:
		return self._rect.width
	
	def get_height(self) -> float:
		return self._rect.width
	
	def get_x(self) -> float:
		return self._rect.x
	
	def get_y(self) -> float:
		return self._rect.y
	
	def _calc_thrust_power(self, direction: int) -> float:
		# https://www.geogebra.org/calculator/vtr4t243
		x = self._body.velocity.y / GLOBAL_SCALE
		decay = self._player_data.thrust_decay
		thrust = self._player_data.thrust
		if x < 0.0:
			return thrust * math.exp(x * direction * decay)
		else:
			return thrust
			a = -x * decay * direction
			return thrust * math.log(a**2 - a + 1) + 1
