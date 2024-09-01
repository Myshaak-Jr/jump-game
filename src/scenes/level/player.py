import os
from typing import override
import pygame
import pymunk
import pymunk.space
from util.my_math import Vec2
from .camera import Camera
from core import PlanetData, PlayerData
import math
from .util import GLOBAL_SCALE, IHasPos
from random import choice
import util.asset_manager as am


__all__ = [
	"Player",
]


class Player(IHasPos):
	def __init__(self, space: pymunk.Space, x: float, y: float, width: float, planet: PlanetData, player_data: PlayerData):
		self._planet = planet
		self._player_data = player_data
		self._color = (255, 0, 0)
		self._alive = True
		self._won = False

		# Load the player sprites
		self._load_sprites()
		
		# Pymunk representation
		self._load_body(space, x, y, width)

		# Apply a force to the right
		self._push_right()

		# Cache for the car sprite
		self._last_zoom = 0
		self._car_cache: pygame.Surface | None = None
		self._wheel_cache: pygame.Surface | None = None

	def _load_body(self, space: pymunk.Space, x: float, y: float, width: float):
		self._SCALE = 1 / 100 * width

		self._CHASSI_WIDTH = 60 * self._SCALE
		self._CHASSI_HEIGHT = 30 * self._SCALE

		self._AXLE_LENGTH = 30 * self._SCALE
		self._AXLE_RADIUS = 3 * self._SCALE
		self._AXLE_ANGLE = 40

		self._WHEEL_RADIUS = 15 * self._SCALE

		self._AXLE1_TANGENT = pymunk.Vec2d(1, 0).rotated(math.radians(-self._AXLE_ANGLE))
		self._AXLE1_P1, self._AXLE1_P2 = -self._AXLE_LENGTH / 2 * self._AXLE1_TANGENT, self._AXLE_LENGTH / 2 * self._AXLE1_TANGENT

		self._AXLE2_TANGENT = pymunk.Vec2d(1, 0).rotated(math.radians(self._AXLE_ANGLE))
		self._AXLE2_P1, self._AXLE2_P2 = -self._AXLE_LENGTH / 2 * self._AXLE2_TANGENT, self._AXLE_LENGTH / 2 * self._AXLE2_TANGENT
		
		size = (self._CHASSI_WIDTH, self._CHASSI_HEIGHT)
		mass = 10
		moment = pymunk.moment_for_box(mass, size)
		self._chassi_b = pymunk.Body(mass, moment)
		self._chassi_s = pymunk.Poly.create_box(self._chassi_b, size)
		self._chassi_s.friction = 0
		self._chassi_b.center_of_gravity = (0, self._CHASSI_HEIGHT * 0.6)
		space.add(self._chassi_b, self._chassi_s)

		mass = 1
		moment = pymunk.moment_for_circle(mass, 0, self._WHEEL_RADIUS)
		self._wheel1_b = pymunk.Body(mass, 2)
		self._wheel1_s = pymunk.Circle(self._wheel1_b, self._WHEEL_RADIUS)
		self._wheel1_s.friction = 1.5
		space.add(self._wheel1_b, self._wheel1_s)

		self._wheel2_b = pymunk.Body(mass, moment)
		self._wheel2_s = pymunk.Circle(self._wheel2_b, self._WHEEL_RADIUS)
		self._wheel2_s.friction = 1.5
		space.add(self._wheel2_b, self._wheel2_s)


		mass = 0.1
		moment = pymunk.moment_for_segment(mass, self._AXLE1_P1, self._AXLE1_P2, self._AXLE_RADIUS)
		self._axle1_b = pymunk.Body(mass, moment)
		self._axle1_s = pymunk.Segment(self._axle1_b, self._AXLE1_P1, self._AXLE1_P2, self._AXLE_RADIUS)
		self._axle1_s.friction = 1.5
		space.add(self._axle1_b, self._axle1_s)

		moment = pymunk.moment_for_segment(mass, self._AXLE2_P1, self._AXLE2_P2, self._AXLE_RADIUS)
		self._axle2_b = pymunk.Body(mass, moment)
		self._axle2_s = pymunk.Segment(self._axle2_b, self._AXLE2_P1, self._AXLE2_P2, self._AXLE_RADIUS)
		self._axle2_s.friction = 1.5
		space.add(self._axle2_b, self._axle2_s)

		self.set_pos(Vec2(x, y))

		j1 = pymunk.PivotJoint(self._chassi_b, self._axle1_b,
			(-(self._CHASSI_WIDTH / 2 - self._AXLE_RADIUS), self._CHASSI_HEIGHT / 2 - self._AXLE_RADIUS),
			self._AXLE1_P2
		)
		j1.collide_bodies = False
		s1 = pymunk.DampedRotarySpring(self._chassi_b, self._axle1_b, 0, 1000, 9)
		space.add(j1, s1)

		j2 = pymunk.PivotJoint(self._chassi_b, self._axle2_b,
			(self._CHASSI_WIDTH / 2 - self._AXLE_RADIUS, self._CHASSI_HEIGHT / 2 - self._AXLE_RADIUS),
			self._AXLE2_P1
		)
		j2.collide_bodies = False
		s2 = pymunk.DampedRotarySpring(self._chassi_b, self._axle2_b, 0, 1000, 9)
		space.add(j2, s2)

		j3 = pymunk.PivotJoint(self._axle1_b, self._wheel1_b, self._AXLE1_P1, (0, 0))
		j3.collide_bodies = False
		space.add(j3)
		j4 = pymunk.PivotJoint(self._axle2_b, self._wheel2_b, self._AXLE2_P2, (0, 0))
		j4.collide_bodies = False
		space.add(j4)
	
	def _load_sprites(self):
		cars = [car for car in os.listdir("assets/image/player/cars/") if car.endswith(".png")]
		wheels = [wheel for wheel in os.listdir("assets/image/player/wheels/") if wheel.endswith(".png")]

		car = choice(cars)
		wheel = choice(wheels)

		self._car = am.get_image(f"assets/image/player/cars/{car}")
		self._wheel = am.get_image(f"assets/image/player/wheels/{wheel}")

	def render(self, screen: pygame.Surface, camera: Camera):
		# Draw the axles
		axle1_p1 = camera.apply_pos(Vec2(self._axle1_b.position + self._AXLE1_P1))
		axle1_p2 = camera.apply_pos(Vec2(self._axle1_b.position + self._AXLE1_P2))
		axle2_p1 = camera.apply_pos(Vec2(self._axle2_b.position + self._AXLE2_P1))
		axle2_p2 = camera.apply_pos(Vec2(self._axle2_b.position + self._AXLE2_P2))
		axle_width = camera.get_zoom() * self._AXLE_RADIUS * 2

		pygame.draw.line(screen, self._color, axle1_p1.to_tuple(), axle1_p2.to_tuple(), int(axle_width))
		pygame.draw.line(screen, self._color, axle2_p1.to_tuple(), axle2_p2.to_tuple(), int(axle_width))

		# Draw the chassi
		chassi_angle = self._chassi_b.angle
		vertices = [v for v in self._chassi_s.get_vertices()]
		vertices = [v.rotated(chassi_angle) for v in vertices]
		vertices = [camera.apply_pos(Vec2(self._chassi_b.position + v)) for v in vertices]

		pygame.draw.polygon(screen, self._color, [v.to_tuple() for v in vertices])

		# Draw the center of gravity
		cog = camera.apply_pos(Vec2(self._chassi_b.local_to_world(self._chassi_b.center_of_gravity)))
		pygame.draw.circle(screen, (0, 0, 255), cog.to_tuple(), 3)

		# Draw the wheels
		wheel_radius = int(camera.get_zoom() * self._WHEEL_RADIUS)
		
		wheel1_screen_pos = camera.apply_pos(Vec2(self._wheel1_b.position))
		angle = self._wheel1_b.angle

		pygame.draw.circle(screen, self._color, wheel1_screen_pos.to_tuple(), wheel_radius)
		pygame.draw.line(screen, (0, 0, 0), wheel1_screen_pos.to_tuple(), (wheel1_screen_pos.x + math.cos(angle) * wheel_radius, wheel1_screen_pos.y + math.sin(angle) * wheel_radius), 2)
		
		wheel2_screen_pos = camera.apply_pos(Vec2(self._wheel2_b.position))
		angle = self._wheel2_b.angle
		pygame.draw.circle(screen, self._color, wheel2_screen_pos.to_tuple(), wheel_radius)
		pygame.draw.line(screen, (0, 0, 0), wheel2_screen_pos.to_tuple(), (wheel2_screen_pos.x + math.cos(angle) * wheel_radius, wheel2_screen_pos.y + math.sin(angle) * wheel_radius), 2)

		return
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

	def set_pos(self, pos: Vec2):
		new_pos = pymunk.Vec2d(pos.x, pos.y)
		self._chassi_b.position = new_pos
		self._axle1_b.position = new_pos + (
			-(self._CHASSI_WIDTH / 2 - self._AXLE_RADIUS) - self._AXLE1_P2.x,
			self._CHASSI_HEIGHT / 2 - self._AXLE1_P2.y - self._AXLE_RADIUS
		)
		self._axle2_b.position = new_pos + (
			self._CHASSI_WIDTH / 2 - self._AXLE2_P1.x - self._AXLE_RADIUS,
			self._CHASSI_HEIGHT / 2 - self._AXLE2_P1.y - self._AXLE_RADIUS
		)

		self._wheel1_b.position = self._axle1_b.position + self._AXLE1_P1
		self._wheel2_b.position = self._axle2_b.position + self._AXLE2_P2

	def get_mass(self) -> float:
		return self._chassi_b.mass + self._wheel1_b.mass + self._wheel2_b.mass + self._axle1_b.mass + self._axle2_b.mass

	def physics_update(self):
		if not self._alive: return
		if self._chassi_b.velocity.x < self._planet.game_speed * GLOBAL_SCALE:
			self._push_right()

		key_state = pygame.key.get_pressed()
		if key_state[pygame.K_SPACE]:
			force = Vec2(0, -self._calc_thrust_power(1) * self.get_mass())
			self._chassi_b.apply_force_at_world_point(force.to_tuple(), self._chassi_b.position)
		 
		elif key_state[pygame.K_LSHIFT]:
			force = Vec2(0, self._calc_thrust_power(-1) * self.get_mass() / 3)
			self._chassi_b.apply_force_at_world_point(force.to_tuple(), self._chassi_b.position)
		
		if key_state[pygame.K_a]:
			self._wheel1_b.angular_velocity = -30
			self._wheel2_b.angular_velocity = -30

		elif key_state[pygame.K_d]:
			self._wheel1_b.angular_velocity = 30
			self._wheel2_b.angular_velocity = 30

	def update(self, level_size: Vec2):
		# if self._chassi_b.velocity.x <= 0.0:
		# 	self._alive = False
		if self._chassi_b.position.y > level_size.y:
			self._alive = False
		
		if self._alive and self._chassi_b.position.x > level_size.x:
			self._won = True
	
	def _push_right(self):
		return
		force = Vec2(10, 0) * self._chassi_b.mass
		self._chassi_b.apply_impulse_at_world_point(force.to_tuple(), self._chassi_b.position)

		#self._body.velocity = self._planet.game_speed * GLOBAL_SCALE, self._body.velocity.y
	
	def is_alive(self) -> bool:
		return self._alive
	
	def has_won(self) -> bool:
		return self._won
	
	@override
	def get_pos(self) -> Vec2:
		return Vec2(self._chassi_b.position.x, self._chassi_b.position.y)
				
	def _calc_thrust_power(self, direction: int) -> float:
		# https://www.geogebra.org/calculator/vtr4t243
		x = self._chassi_b.velocity.y / GLOBAL_SCALE
		decay = self._player_data.thrust_decay
		thrust = self._player_data.thrust
		if x < 0.0:
			return thrust * math.exp(x * direction * decay)
		else:
			return thrust
			a = -x * decay * direction
			return thrust * math.log(a**2 - a + 1) + 1
