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
		self._max_fuel = 10
		self._fuel = self._max_fuel
		self._fuel_regen_speed = 20

		# Wheels
		self._wheel_speed = 50
		self._wheel_friction = 1.5

		# Load the player sprites
		self._load_sprites()

		# On ground
		self._on_ground: dict[pymunk.Shape, bool] = {}

		# Pymunk representation
		self._load_body(space, x, y)

		handler = space.add_collision_handler(CollisionType.PLAYER.value, CollisionType.GROUND.value)
		handler.begin = self._hit_ground
		handler.separate = self._separate_ground

		self.point_left: Vec2 | None = None
		self.point_right: Vec2 | None = None
		self.force_left: Vec2 | None = None
		self.force_right: Vec2 | None = None

		# Cache for the car sprite
		self._last_zoom = 0
		self._car_cache: pygame.Surface | None = None
		self._wheel_cache: pygame.Surface | None = None

	def _hit_ground(self, arbiter: pymunk.Arbiter, space: pymunk.Space, data: dict[str, Any]) -> bool:
		if arbiter.normal.y > 0.3:
			self._on_ground[arbiter.shapes[0]] = True
		return True
	
	def _separate_ground(self, arbiter: pymunk.Arbiter, space: pymunk.Space, data: dict[str, Any]) -> bool:
		self._on_ground[arbiter.shapes[0]] = False
		return True

	def is_on_ground(self) -> bool:
		return any(self._on_ground.values())

	def _load_body(self, space: pymunk.Space, x: float, y: float):
		self._scale = 1 / 100 * 6

		self._chassi_width = 80 * self._scale
		self._chassi_height = 60 * self._scale

		self._axle_lenght = 30 * self._scale
		self._axle_radius = 3 * self._scale
		self._axle_angle = 40

		self._wheel_radius = 20 * self._scale

		self._left_axle_tangent = pymunk.Vec2d(1, 0).rotated(math.radians(-self._axle_angle))
		self._left_axle_p1, self._left_axle_p2 = -self._axle_lenght / 2 * self._left_axle_tangent, self._axle_lenght / 2 * self._left_axle_tangent

		self._right_axle_tangent = pymunk.Vec2d(1, 0).rotated(math.radians(self._axle_angle))
		self._right_axle_p1, self._right_axle_p2 = -self._axle_lenght / 2 * self._right_axle_tangent, self._axle_lenght / 2 * self._right_axle_tangent

		SPRING_STIFFNESS = 2000
		SPRING_DAMPING = 20
		
		mass = 20
		moment = pymunk.moment_for_box(mass, (
			self._chassi_width + abs(self._left_axle_tangent.x) * self._axle_lenght + abs(self._right_axle_tangent.x) * self._axle_lenght,
			self._chassi_height
		))
		self._chassi_b = pymunk.Body(mass, moment)
		self._chassi_s = pymunk.Poly.create_box(self._chassi_b, (self._chassi_width, self._chassi_height))
		self._chassi_s.friction = 0.7
		self._chassi_b.center_of_gravity = (0, self._chassi_height * 0.6)
		self._chassi_s.collision_type = CollisionType.PLAYER.value
		space.add(self._chassi_b, self._chassi_s)

		mass = 2
		moment = pymunk.moment_for_circle(mass, 0, self._wheel_radius)
		self.left_wheel_b = pymunk.Body(mass, 2)
		self.left_wheel_s = pymunk.Circle(self.left_wheel_b, self._wheel_radius)
		self.left_wheel_s.friction = self._wheel_friction
		self.left_wheel_s.collision_type = CollisionType.PLAYER.value
		space.add(self.left_wheel_b, self.left_wheel_s)

		self._right_wheel_b = pymunk.Body(mass, moment)
		self._right_wheel_s = pymunk.Circle(self._right_wheel_b, self._wheel_radius)
		self._right_wheel_s.friction = self._wheel_friction
		self._right_wheel_s.collision_type = CollisionType.PLAYER.value
		space.add(self._right_wheel_b, self._right_wheel_s)

		mass = 0.1
		moment = pymunk.moment_for_segment(mass, self._left_axle_p1, self._left_axle_p2, self._axle_radius)
		self._left_axle_b = pymunk.Body(mass, moment)
		self._left_axle_s = pymunk.Segment(self._left_axle_b, self._left_axle_p1, self._left_axle_p2, self._axle_radius)
		self._left_axle_s.friction = 1.5
		space.add(self._left_axle_b, self._left_axle_s)

		moment = pymunk.moment_for_segment(mass, self._right_axle_p1, self._right_axle_p2, self._axle_radius)
		self._right_axle_b = pymunk.Body(mass, moment)
		self._right_axle_s = pymunk.Segment(self._right_axle_b, self._right_axle_p1, self._right_axle_p2, self._axle_radius)
		self._right_axle_s.friction = 1.5
		space.add(self._right_axle_b, self._right_axle_s)

		self.set_pos(Vec2(x, y))

		j1 = pymunk.PivotJoint(self._chassi_b, self._left_axle_b,
			(-(self._chassi_width / 2 - self._axle_radius), self._chassi_height / 2 - self._axle_radius),
			self._left_axle_p2
		)
		j1.collide_bodies = False
		s1 = pymunk.DampedRotarySpring(self._chassi_b, self._left_axle_b, 0, SPRING_STIFFNESS, SPRING_DAMPING)
		space.add(j1, s1)

		j2 = pymunk.PivotJoint(self._chassi_b, self._right_axle_b,
			(self._chassi_width / 2 - self._axle_radius, self._chassi_height / 2 - self._axle_radius),
			self._right_axle_p1
		)
		j2.collide_bodies = False
		s2 = pymunk.DampedRotarySpring(self._chassi_b, self._right_axle_b, 0, SPRING_STIFFNESS, SPRING_DAMPING)
		space.add(j2, s2)

		j3 = pymunk.PivotJoint(self._left_axle_b, self.left_wheel_b, self._left_axle_p1, (0, 0))
		j3.collide_bodies = False
		space.add(j3)
		j4 = pymunk.PivotJoint(self._right_axle_b, self._right_wheel_b, self._right_axle_p2, (0, 0))
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
		left_axle_p1 = camera.apply_pos(Vec2(self._left_axle_b.local_to_world(self._left_axle_p1)))
		left_axle_p2 = camera.apply_pos(
			Vec2(
				self._chassi_b.local_to_world(
					(
						-self._chassi_width / 2 + self._axle_radius,
						self._chassi_height / 2 - self._axle_radius
					)
				)
			)
		)
		right_axle_p1 = camera.apply_pos(
			Vec2(
				self._chassi_b.local_to_world(
					(
						self._chassi_width / 2 - self._axle_radius,
						self._chassi_height / 2 - self._axle_radius
					)
				)
			)
		)
		right_axle_p2 = camera.apply_pos(Vec2(self._right_axle_b.local_to_world(self._right_axle_p2)))
		axle_width = camera.get_zoom() * self._axle_radius * 2

		pygame.draw.line(screen, "#D4D7D9", left_axle_p1.to_tuple(), left_axle_p2.to_tuple(), int(axle_width))
		pygame.draw.line(screen, "#D4D7D9", right_axle_p1.to_tuple(), right_axle_p2.to_tuple(), int(axle_width))

		# Draw the chassi

		if self._last_zoom != camera.get_zoom() or self._car_cache is None:
			self._last_zoom = camera.get_zoom()
			aspect_ratio = self._car.get_width() / self._car.get_height()
			new_height = int(camera.get_zoom() * self._chassi_height)
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
		wheel_radius = int(camera.get_zoom() * (self._wheel_radius * 1.1)) # 1.1 because the wheel image is a bit smaller than the actual wheel

		if self._last_zoom != camera.get_zoom() or self._wheel_cache is None:
			self._last_zoom = camera.get_zoom()
			self._wheel_cache = pygame.transform.scale(self._wheel, (wheel_radius * 2, wheel_radius * 2))
			
		left_wheel_screen_pos = camera.apply_pos(Vec2(self.left_wheel_b.position))
		left_wheel_angle = self.left_wheel_b.angle
		left_wheel_sprite = pygame.transform.rotate(self._wheel_cache, -math.degrees(left_wheel_angle))
		left_wheel_x, left_wheel_y = left_wheel_sprite.get_size()
		left_wheel_x = left_wheel_screen_pos.x - left_wheel_x / 2
		left_wheel_y = left_wheel_screen_pos.y - left_wheel_y / 2

		screen.blit(left_wheel_sprite, (left_wheel_x, left_wheel_y))

		right_wheel_screen_pos = camera.apply_pos(Vec2(self._right_wheel_b.position))
		right_wheel_angle = self._right_wheel_b.angle
		right_wheel_sprite = pygame.transform.rotate(self._wheel_cache, -math.degrees(right_wheel_angle))
		right_wheel_x, right_wheel_y = right_wheel_sprite.get_size()
		right_wheel_x = right_wheel_screen_pos.x - right_wheel_x / 2
		right_wheel_y = right_wheel_screen_pos.y - right_wheel_y / 2
		
		screen.blit(right_wheel_sprite, (right_wheel_x, right_wheel_y))

		if self.point_left is not None and self.force_left is not None:
			pygame.draw.line(screen, (0, 255, 0), camera.apply_pos(self.point_left).to_tuple(), camera.apply_pos(self.point_left + self.force_left).to_tuple(), 5)

		if self.point_right is not None and self.force_right is not None:
			pygame.draw.line(screen, (0, 255, 0), camera.apply_pos(self.point_right).to_tuple(), camera.apply_pos(self.point_right + self.force_right).to_tuple(), 5)

	def render_fuel_bar(self, screen: pygame.Surface):
		x = 10
		y = 10
		width = app_state.get_width() / 4
		height = 20

		pygame.draw.rect(screen, (0, 0, 0), (x-3, y-3, width+6, height+6))

		fuel_width = width * self._fuel / self._max_fuel
		pygame.draw.rect(screen, (0, 255, 0), (x, y, fuel_width, height))

	def set_pos(self, pos: Vec2):
		new_pos = pymunk.Vec2d(pos.x, pos.y)
		self._chassi_b.position = new_pos
		self._left_axle_b.position = new_pos + (
			-(self._chassi_width / 2 - self._axle_radius) - self._left_axle_p2.x,
			self._chassi_height / 2 - self._left_axle_p2.y - self._axle_radius
		)
		self._right_axle_b.position = new_pos + (
			self._chassi_width / 2 - self._right_axle_p1.x - self._axle_radius,
			self._chassi_height / 2 - self._right_axle_p1.y - self._axle_radius
		)

		self.left_wheel_b.position = self._left_axle_b.position + self._left_axle_p1
		self._right_wheel_b.position = self._right_axle_b.position + self._right_axle_p2

	def get_mass(self) -> float:
		return self._chassi_b.mass + self.left_wheel_b.mass + self._right_wheel_b.mass + self._left_axle_b.mass + self._right_axle_b.mass

	def physics_update(self, dt: float):
		if not self._alive: return

		# Modify the fuel
		if self.is_on_ground():
			self._fuel += self._fuel_regen_speed * dt
			self._fuel = min(self._fuel, self._max_fuel)

		# Handle the input
		key_state = pygame.key.get_pressed()
		# if key_state[pygame.K_SPACE] and self._fuel > 0:
		# 	force = self._calc_thrust_up_force()
		# 	point = pymunk.Vec2d(0, -self._chassi_height).rotated(self._chassi_b.angle) + self._chassi_b.position
		# 	self._chassi_b.apply_force_at_world_point(pymunk.Vec2d(0, force), point)

		# elif key_state[pygame.K_LSHIFT] and self._fuel > 0:
		# 	force = self._player_data.thrust_down * self.get_mass()
		# 	point = pymunk.Vec2d(0, self._chassi_height).rotated(self._chassi_b.angle) + self._chassi_b.position
		# 	self._chassi_b.apply_force_at_world_point(pymunk.Vec2d(0, force), point)

		# 	self._fuel -= force / (self._player_data.thrust_up * self.get_mass())
		# 	self._fuel = max(self._fuel, 0)

		# if self._chassi_b.velocity.x < self._planet.game_speed:
		# 	point = self._chassi_b.local_to_world(self._chassi_b.center_of_gravity)
		# 	force = pymunk.Vec2d(self._planet.game_acceleration, 0) * self.get_mass()
		# 	self._chassi_b.apply_force_at_world_point(force, point)

		if key_state[pygame.K_a]:
			self._chassi_b.position -= Vec2(20 * dt, 0)
		if key_state[pygame.K_d]:
			self._chassi_b.position += Vec2(20 * dt, 0)
		if key_state[pygame.K_w]:
			self._chassi_b.position -= Vec2(0, 20 * dt)
		if key_state[pygame.K_s]:
			self._chassi_b.position += Vec2(0, 20 * dt)

		self._chassi_b.velocity = 0, 0

		if key_state[pygame.K_q]:
			self._chassi_b.angle += 0.1
		if key_state[pygame.K_e]:
			self._chassi_b.angle -= 0.1
		if key_state[pygame.K_SPACE]:
			self._settle_angle()
		else:
			self._chassi_b.angular_velocity = 0
			self.point_left = None
			self.point_right = None
			self.force_left = None
			self.force_right = None
			self.direction = 0

	def _settle_angle(self):
		angle = self._chassi_b.angle % (2 * math.pi)

		if angle > math.pi:
			angle -= 2 * math.pi

		print(angle)

		#if abs(angle) < 0.1: return
		a = 0.1
		c = 0.7
		d = 0.2

		angle_mult = math.sin(abs(angle / 2))
		speed_mult = 1 # c*exponensial_logarithmic_function(-a*abs(self._chassi_b.angular_velocity)) + d

		direction = 1 if angle > 0 else -1
		force_strength = 300 * angle_mult * speed_mult * direction

		x_offset = self._chassi_width / 2

		left_point = self._chassi_b.center_of_gravity + pymunk.Vec2d(-x_offset, 0)
		right_point = self._chassi_b.center_of_gravity + pymunk.Vec2d(x_offset, 0)

		self._chassi_b.apply_force_at_local_point(pymunk.Vec2d(0, force_strength), left_point)
		self._chassi_b.apply_force_at_local_point(pymunk.Vec2d(0, -force_strength), right_point)

		self.point_left = Vec2(left_point).rotated(self._chassi_b.angle) + self._chassi_b.position
		self.point_right = Vec2(right_point).rotated(self._chassi_b.angle) + self._chassi_b.position
		self.force_left = Vec2(0, force_strength).rotated(self._chassi_b.angle)
		self.force_right = Vec2(0, -force_strength).rotated(self._chassi_b.angle)

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
		c = 0.05
		x = -self._chassi_b.velocity.x
		relative_x = (1-(a+b))/(1+math.exp(-x * c))+a
		relative_y = camera.get_relative_position().y
		camera.set_relative_position(Vec2(relative_x, relative_y))
		
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
