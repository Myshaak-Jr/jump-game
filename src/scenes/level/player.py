import os
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
from random import choice
import util.asset_manager as am


__all__ = [
	"Player",
]

# Constants, relative to width of the car
WHEEL_1_SIZE = 0.3
WHEEL_1_X = 0.185 - WHEEL_1_SIZE / 2

WHEEL_2_SIZE = 0.3
WHEEL_2_X = 0.779 - WHEEL_2_SIZE / 2

GROUND_CLEARANCE = 0.1

class Player(IHasRect):
	def __init__(self, space: pymunk.Space, x: float, y: float, width: float, planet: PlanetData, player_data: PlayerData):
		self._planet = planet
		self._player_data = player_data
		self._color = (255, 0, 0)
		self._alive = True

		# Load the player sprites
		self._load_sprites(x, y, width)
		
		# Pymunk representation
		self._body = pymunk.Body()  # Mass and moment of inertia
		self._body.position = (self._rect.x + self._rect.width / 2, self._rect.y + self._rect.height / 2)
		self._shape = pymunk.Circle(self._body, self._rect.width / 2)
		self._shape.mass = 1
		self._shape.elasticity = 0.5
		self._shape.friction = 0.5

		# Collision type to identify player
		self._shape.collision_type = 1
		
		# Add the shape to the space
		space.add(self._body, self._shape)

		# Apply a force to the right
		self._push_right()

		# Cache for the car sprite
		self._last_zoom = 0
		self._car_cache: pygame.Surface | None = None
		self._wheel_cache: pygame.Surface | None = None

	
	def _load_sprites(self, x: float, y: float, width: float):
		cars = [car for car in os.listdir("assets/image/player/cars/") if car.endswith(".png")]
		wheels = [wheel for wheel in os.listdir("assets/image/player/wheels/") if wheel.endswith(".png")]

		car = choice(cars)
		wheel = choice(wheels)

		self._car = am.get_image(f"assets/image/player/cars/{car}")
		self._wheel = am.get_image(f"assets/image/player/wheels/{wheel}")

		car_size = self._car.get_size()
		new_height = width * car_size[1] / car_size[0] # car height
		new_height += width * GROUND_CLEARANCE # add some space for the wheels

		self._rect = pygame.FRect(x - width / 2, y - new_height, width, new_height)

	def render(self, screen: pygame.Surface, camera: Camera):
		if camera.clip(self): return
		rect = camera.apply(self)
		
		zoom = camera.get_zoom()
		
		if zoom != self._last_zoom or self._car_cache is None or self._wheel_cache is None:
			new_width = int(self._rect.width * zoom)
			new_height = int((self._rect.height - self._rect.width * GROUND_CLEARANCE) * zoom)
			self._car_cache = pygame.transform.scale(self._car, (new_width, new_height))
			self._wheel_cache = pygame.transform.scale(self._wheel, (int(WHEEL_1_SIZE * new_width), int(WHEEL_1_SIZE * new_width)))
			self._last_zoom = int(zoom)
		
		# Draw the car
		screen.blit(self._car_cache, rect.topleft)

		# Draw the wheels
		screen.blit(self._wheel_cache, (int(rect.x + rect.width * WHEEL_1_X), rect.bottom - self._wheel_cache.get_height()))
		screen.blit(self._wheel_cache, (int(rect.x + rect.width * WHEEL_2_X), rect.bottom - self._wheel_cache.get_height()))
	
	def render_bounds(self, screen: pygame.Surface, camera: Camera):
		if camera.clip(self): return
		original_rect = pygame.FRect(self._rect.x, self._rect.y, self._rect.width, self._rect.width)

		rect = camera.apply_rect(original_rect)
		
		# Draw rotation
		angle = self._body.angle
		pygame.draw.line(screen, (255, 0, 0), rect.center, (rect.centerx + rect.width / 2 * math.cos(angle), rect.centery + rect.width / 2 * math.sin(angle)), 3)

		pygame.draw.circle(screen, (255, 0, 0), rect.center, int(rect.width / 2), 3)
		pygame.draw.circle(screen, (255, 0, 0), rect.center, 5)


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
		
		elif key_state[pygame.K_LSHIFT]:
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
