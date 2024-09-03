import os
from typing import Any, override
import pygame
import pymunk
import pymunk.space
from util.my_math import Vec2, exponensial_logarithmic_function
from .camera import Camera
from core import PlanetData, PlayerData, app_state
import math
from .util import CollisionType, IHasPos
from random import choice
import util.asset_manager as am


__all__ = [
	"Player",
]


class Player(IHasPos):
	def __init__(self, space: pymunk.Space, x: float, y: float, planet: PlanetData, player_data: PlayerData):
		self._planet = planet
		self._player_data = player_data
		self._color = (255, 0, 0)
		self._alive = True
		self._won = False

		# Fuel
		self._MAX_FUEL = 8
		self._fuel = self._MAX_FUEL

		# Load the player sprites
		self._load_sprites()
		
		# Pymunk representation
		self._load_body(space, x, y)

		handler = space.add_collision_handler(CollisionType.PLAYER.value, CollisionType.GROUND.value)
		handler.post_solve = self._hit_ground

		# Apply a force to the right
		self._push_right()

		# Cache for the car sprite
		self._last_zoom = 0
		self._car_cache: pygame.Surface | None = None
		self._wheel_cache: pygame.Surface | None = None

	def _hit_ground(self, arbiter: pymunk.Arbiter, space: pymunk.Space, data: dict[str, Any]) -> bool:
		if arbiter.normal.y > 0.8:
			self._fuel = self._MAX_FUEL
		return True

	def _load_body(self, space: pymunk.Space, x: float, y: float):
		self._SCALE = 1 / 100 * 6

		self._CHASSI_WIDTH = 80 * self._SCALE
		self._CHASSI_HEIGHT = 60 * self._SCALE

		self._AXLE_LENGTH = 30 * self._SCALE
		self._AXLE_RADIUS = 3 * self._SCALE
		self._AXLE_ANGLE = 40

		self._WHEEL_RADIUS = 20 * self._SCALE

		self._AXLE1_TANGENT = pymunk.Vec2d(1, 0).rotated(math.radians(-self._AXLE_ANGLE))
		self._AXLE1_P1, self._AXLE1_P2 = -self._AXLE_LENGTH / 2 * self._AXLE1_TANGENT, self._AXLE_LENGTH / 2 * self._AXLE1_TANGENT

		self._AXLE2_TANGENT = pymunk.Vec2d(1, 0).rotated(math.radians(self._AXLE_ANGLE))
		self._AXLE2_P1, self._AXLE2_P2 = -self._AXLE_LENGTH / 2 * self._AXLE2_TANGENT, self._AXLE_LENGTH / 2 * self._AXLE2_TANGENT
		
		mass = 20
		moment = pymunk.moment_for_box(mass, (
			self._CHASSI_WIDTH + abs(self._AXLE1_TANGENT.x) * self._AXLE_LENGTH + abs(self._AXLE2_TANGENT.x) * self._AXLE_LENGTH,
			self._CHASSI_HEIGHT
		))
		self._chassi_b = pymunk.Body(mass, moment)
		self._chassi_s = pymunk.Poly.create_box(self._chassi_b, (self._CHASSI_WIDTH, self._CHASSI_HEIGHT))
		self._chassi_s.friction = 0.7
		self._chassi_b.center_of_gravity = (0, self._CHASSI_HEIGHT * 0.6)
		self._chassi_s.collision_type = CollisionType.PLAYER.value
		space.add(self._chassi_b, self._chassi_s)

		mass = 2
		moment = pymunk.moment_for_circle(mass, 0, self._WHEEL_RADIUS)
		self._wheel1_b = pymunk.Body(mass, 2)
		self._wheel1_s = pymunk.Circle(self._wheel1_b, self._WHEEL_RADIUS)
		self._wheel1_s.friction = 1.5
		self._wheel1_s.collision_type = CollisionType.PLAYER.value
		space.add(self._wheel1_b, self._wheel1_s)

		self._wheel2_b = pymunk.Body(mass, moment)
		self._wheel2_s = pymunk.Circle(self._wheel2_b, self._WHEEL_RADIUS)
		self._wheel2_s.friction = 1.5
		self._wheel2_s.collision_type = CollisionType.PLAYER.value
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
		s1 = pymunk.DampedRotarySpring(self._chassi_b, self._axle1_b, 0, 2000, 9)
		space.add(j1, s1)

		j2 = pymunk.PivotJoint(self._chassi_b, self._axle2_b,
			(self._CHASSI_WIDTH / 2 - self._AXLE_RADIUS, self._CHASSI_HEIGHT / 2 - self._AXLE_RADIUS),
			self._AXLE2_P1
		)
		j2.collide_bodies = False
		s2 = pymunk.DampedRotarySpring(self._chassi_b, self._axle2_b, 0, 2000, 9)
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
		axle1_p1 = camera.apply_pos(Vec2(self._axle1_b.local_to_world(self._AXLE1_P1)))
		axle1_p2 = camera.apply_pos(
			Vec2(
				self._chassi_b.local_to_world(
					(
						-self._CHASSI_WIDTH / 2 + self._AXLE_RADIUS,
						self._CHASSI_HEIGHT / 2 - self._AXLE_RADIUS
					)
				)
			)
		)
		axle2_p1 = camera.apply_pos(
			Vec2(
				self._chassi_b.local_to_world(
					(
						self._CHASSI_WIDTH / 2 - self._AXLE_RADIUS,
						self._CHASSI_HEIGHT / 2 - self._AXLE_RADIUS
					)
				)
			)
		)
		axle2_p2 = camera.apply_pos(Vec2(self._axle2_b.local_to_world(self._AXLE2_P2)))
		axle_width = camera.get_zoom() * self._AXLE_RADIUS * 2

		pygame.draw.line(screen, "#D4D7D9", axle1_p1.to_tuple(), axle1_p2.to_tuple(), int(axle_width))
		pygame.draw.line(screen, "#D4D7D9", axle2_p1.to_tuple(), axle2_p2.to_tuple(), int(axle_width))

		# Draw the chassi

		if self._last_zoom != camera.get_zoom() or self._car_cache is None:
			self._last_zoom = camera.get_zoom()
			aspect_ratio = self._car.get_width() / self._car.get_height()
			new_height = int(camera.get_zoom() * self._CHASSI_HEIGHT)
			new_width = int(new_height * aspect_ratio)
			self._car_cache = pygame.transform.scale(self._car, (new_width, new_height))
		
		chassi_screen_pos = camera.apply_pos(Vec2(self._chassi_b.position))
		chassi_angle = self._chassi_b.angle
		chassi_sprite = pygame.transform.rotate(self._car_cache, -math.degrees(chassi_angle))
		chassi_x, chassi_y = chassi_sprite.get_size()
		chassi_x = chassi_screen_pos.x - chassi_x / 2
		chassi_y = chassi_screen_pos.y - chassi_y / 2

		screen.blit(chassi_sprite, (chassi_x, chassi_y))

		# vertices = [v for v in self._chassi_s.get_vertices()]
		# vertices = [v.rotated(chassi_angle) for v in vertices]
		# vertices = [camera.apply_pos(Vec2(self._chassi_b.position + v)) for v in vertices]

		# pygame.draw.polygon(screen, self._color, [v.to_tuple() for v in vertices])

		# # Draw the center of gravity
		# cog = camera.apply_pos(Vec2(self._chassi_b.local_to_world(self._chassi_b.center_of_gravity)))
		# pygame.draw.circle(screen, (0, 0, 255), cog.to_tuple(), 3)

		# Draw the wheels
		wheel_radius = int(camera.get_zoom() * (self._WHEEL_RADIUS * 1.1)) # 1.1 because the wheel image is a bit smaller than the actual wheel

		if self._last_zoom != camera.get_zoom() or self._wheel_cache is None:
			self._last_zoom = camera.get_zoom()
			self._wheel_cache = pygame.transform.scale(self._wheel, (wheel_radius * 2, wheel_radius * 2))
		
		wheel1_screen_pos = camera.apply_pos(Vec2(self._wheel1_b.position))
		wheel1_angle = self._wheel1_b.angle
		wheel1_sprite = pygame.transform.rotate(self._wheel_cache, -math.degrees(wheel1_angle))
		wheel1_x, wheel1_y = wheel1_sprite.get_size()
		wheel1_x = wheel1_screen_pos.x - wheel1_x / 2
		wheel1_y = wheel1_screen_pos.y - wheel1_y / 2

		screen.blit(wheel1_sprite, (wheel1_x, wheel1_y))

		wheel2_screen_pos = camera.apply_pos(Vec2(self._wheel2_b.position))
		wheel2_angle = self._wheel2_b.angle
		wheel2_sprite = pygame.transform.rotate(self._wheel_cache, -math.degrees(wheel2_angle))
		wheel2_x, wheel2_y = wheel2_sprite.get_size()
		wheel2_x = wheel2_screen_pos.x - wheel2_x / 2
		wheel2_y = wheel2_screen_pos.y - wheel2_y / 2
		
		screen.blit(wheel2_sprite, (wheel2_x, wheel2_y))

		# left_point, right_point, force_left, force_right = self._get_force_points()
		# left_point_screen = camera.apply_pos(Vec2(left_point))
		# right_point_screen = camera.apply_pos(Vec2(right_point))
		# force_left_screen = camera.apply_pos(Vec2(left_point + force_left/1000))
		# force_right_screen = camera.apply_pos(Vec2(right_point + force_right/1000))

		# pygame.draw.line(screen, (255, 0, 0), left_point_screen.to_tuple(), force_left_screen.to_tuple(), 2)
		# pygame.draw.line(screen, (255, 0, 0), right_point_screen.to_tuple(), force_right_screen.to_tuple(), 2)

	def render_fuel_bar(self, screen: pygame.Surface):
		x = 10
		y = 10
		width = app_state.get_width() / 4
		height = 20

		pygame.draw.rect(screen, (0, 0, 0), (x-3, y-3, width+6, height+6))

		fuel_width = width * self._fuel / self._MAX_FUEL
		pygame.draw.rect(screen, (0, 255, 0), (x, y, fuel_width, height))

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

	def _get_force_points(self) -> tuple[pymunk.Vec2d, pymunk.Vec2d, pymunk.Vec2d, pymunk.Vec2d]:
		a = 0.1
		c = 0.7
		d = 0.2

		x_offset = self._CHASSI_WIDTH / 2
		y_offset = 0

		left_point = pymunk.Vec2d(-x_offset, y_offset).rotated(self._chassi_b.angle) + self._chassi_b.position
		right_point = pymunk.Vec2d(x_offset, y_offset).rotated(self._chassi_b.angle) + self._chassi_b.position

		force_strength = self._calc_thrust_up_force() / 2

		angle_mult_left = (1 - math.sin(self._chassi_b.angle)) / 2
		speed_mult_left = c*exponensial_logarithmic_function(-a*self._chassi_b.angular_velocity) + d
		force_left = pymunk.Vec2d(0, force_strength) * angle_mult_left * speed_mult_left

		angle_mult_right = (1 + math.sin(self._chassi_b.angle)) / 2
		speed_mult_right = c*exponensial_logarithmic_function(a*self._chassi_b.angular_velocity) + d
		force_right = pymunk.Vec2d(0, force_strength) * angle_mult_right * speed_mult_right

		return left_point, right_point, force_left, force_right

	def physics_update(self, dt: float):
		if not self._alive: return
		if self._chassi_b.velocity.x < self._planet.game_speed:
			self._push_right()

		key_state = pygame.key.get_pressed()
		if key_state[pygame.K_SPACE] and self._fuel > 0:
			left_point, right_point, force_left, force_right = self._get_force_points()
			self._chassi_b.apply_force_at_world_point(force_left, left_point)
			self._chassi_b.apply_force_at_world_point(force_right, right_point)

			if self._chassi_b.velocity.y < 0.0:
				self._fuel -= math.exp(-self._chassi_b.velocity.y * self._player_data.thrust_decay) * dt
			else:
				self._fuel -= dt
			self._fuel = max(0, self._fuel)

		elif key_state[pygame.K_LSHIFT] and self._fuel > 0:
			point = pymunk.Vec2d(0, self._CHASSI_HEIGHT).rotated(self._chassi_b.angle) + self._chassi_b.position

			thrust = self._player_data.thrust_down * self.get_mass()
			self._chassi_b.apply_force_at_world_point(pymunk.Vec2d(0, thrust), point)

			self._fuel -= dt
			self._fuel = max(0, self._fuel)
		
		if key_state[pygame.K_a]:
			self._wheel1_b.angular_velocity = -30
			self._wheel2_b.angular_velocity = -30

		elif key_state[pygame.K_d]:
			self._wheel1_b.angular_velocity = 30
			self._wheel2_b.angular_velocity = 30

	def update(self, level_size: Vec2, camera: Camera):
		# cap the angular velocity
		self._chassi_b.angular_velocity = max(min(self._chassi_b.angular_velocity, 10), -10)

		# if self._chassi_b.velocity.x <= 0.0:
		# 	self._alive = False
		if self._chassi_b.position.y > level_size.y:
			self._alive = False
		
		if self._alive and self._chassi_b.position.x > level_size.x:
			self._won = True

		# update relative position
		a = 0.2
		b = 0.3
		c = 0.1
		x = -self._chassi_b.velocity.x
		relative_x = (1-(a+b))/(1+math.exp(-x * c))+a
		relative_y = camera.get_relative_position().y
		camera.set_relative_position(Vec2(relative_x, relative_y))
	
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
	
	def _calc_thrust_up_force(self) -> float:
		# https://www.geogebra.org/calculator/vtr4t243
		x = self._chassi_b.velocity.y
		thrust = self._player_data.thrust_up * self.get_mass()
		if x < 0.0:
			return -thrust * math.exp(x * self._player_data.thrust_decay)
		else:
			return -thrust
