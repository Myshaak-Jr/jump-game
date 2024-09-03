from typing import override
import pymunk
import pymunk.pygame_util
import pygame
from core import IScene, app_state
import math


class ThrusterTestScene(IScene):
	def __init__(self):
		self._space = pymunk.Space()
		self._space.gravity = 0, 0

		self._pivot_b = pymunk.Body(body_type=pymunk.Body.STATIC)
		self._pivot_b.position = pymunk.Vec2d(app_state.get_width() // 2, app_state.get_height() // 2)
		self._pivot_s = pymunk.Circle(self._pivot_b, 5)
		self._space.add(self._pivot_b, self._pivot_s)

		mass = 20
		self._p1 = pymunk.Vec2d(-50, 0)
		self._p2 = pymunk.Vec2d(+50, 0)
		moment = pymunk.moment_for_segment(mass, self._p1, self._p2, 5)
		self._swing_b = pymunk.Body(mass, moment)
		self._swing_s = pymunk.Segment(self._swing_b, self._p1, self._p2, 5)
		self._swing_s.friction = 1
		self._space.add(self._swing_b, self._swing_s)

		self._swing_b.position = self._pivot_b.position

		joint = pymunk.PinJoint(self._pivot_b, self._swing_b, (0, 0), (0, 0))
		joint.collide_bodies = False
		self._space.add(joint)

		self._manual = False


	@override
	def on_enter(self) -> None:
		pass

	@override
	def on_exit(self) -> None:
		pass

	@override
	def handle_event(self, event: pygame.event.Event) -> None:
		pass

	def _calc_thrust_up_force(self) -> float:
		return -5000

	def _get_force_points(self) -> tuple[pymunk.Vec2d, pymunk.Vec2d, pymunk.Vec2d, pymunk.Vec2d]:
		x_offset = 50
		y_offset = 0

		left_point = pymunk.Vec2d(-x_offset, y_offset).rotated(self._swing_b.angle) + self._swing_b.position
		right_point = pymunk.Vec2d(x_offset, y_offset).rotated(self._swing_b.angle) + self._swing_b.position

		force_strength = self._calc_thrust_up_force() / 2

		angle_mult_left = (1 - math.sin(self._swing_b.angle)) / 2
		speed_mult_left = math.exp(-self._swing_b.angular_velocity)
		force_left = pymunk.Vec2d(0, force_strength) * angle_mult_left * speed_mult_left

		angle_mult_right = (1 + math.sin(self._swing_b.angle)) / 2
		speed_mult_right = math.exp(self._swing_b.angular_velocity)
		force_right = pymunk.Vec2d(0, force_strength) * angle_mult_right * speed_mult_right

		return left_point, right_point, force_left, force_right

	@override
	def update(self, dt: float) -> None:
		key_state = pygame.key.get_pressed()

		if key_state[pygame.K_a]:
			self._swing_b.angular_velocity = -1
			self._manual = True
		elif key_state[pygame.K_d]:
			self._swing_b.angular_velocity = 1
			self._manual = True
		
		if self._manual and not key_state[pygame.K_a] and not key_state[pygame.K_d]:
			self._swing_b.angular_velocity = 0
			self._manual = False

		if not self._manual and key_state[pygame.K_SPACE]:
			left_point, right_point, force_left, force_right = self._get_force_points()
			self._swing_b.apply_force_at_world_point(force_left, left_point)
			self._swing_b.apply_force_at_world_point(force_right, right_point)

		self._space.step(dt)

	@override
	def render(self, screen: pygame.Surface) -> None:
		screen.fill(pygame.Color("white"))
		draw_options = pymunk.pygame_util.DrawOptions(screen)
		self._space.debug_draw(draw_options)

		color = pygame.Color("blue") if self._swing_b.angular_velocity > 0 else pygame.Color("red")

		left_point, right_point, force_left, force_right = self._get_force_points()
		pygame.draw.line(screen, color, left_point, left_point + force_left/100)
		pygame.draw.line(screen, color, right_point, right_point + force_right/100)

		pygame.display.flip()

	@override
	@classmethod
	def get_name(cls) -> str:
		return "thruster_test"