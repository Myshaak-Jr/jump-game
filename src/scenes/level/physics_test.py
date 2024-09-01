from math import radians
from typing import override
import pymunk
import pymunk.pygame_util
import pygame
from pymunk.vec2d import Vec2d
from core import IScene, app_state


def floor(space: pymunk.Space):
	floor_segment = pymunk.Segment(space.static_body, (0, 300), (app_state.get_width(), 300), 5)
	floor_segment.friction = 1.0
	space.add(floor_segment)

	vs1: list[tuple[float, float]] = [(0, 300), (50, 300), (0, 200)]
	b1 = pymunk.Body(body_type=pymunk.Body.STATIC)
	s1 = pymunk.Poly(b1, vs1)
	s1.friction = 1

	space.add(b1, s1)

	vs2: list[tuple[float, float]] = [(app_state.get_width(), 300), (app_state.get_width() - 50, 300), (app_state.get_width(), 200)]
	b2 = pymunk.Body(body_type=pymunk.Body.STATIC)
	s2 = pymunk.Poly(b2, vs2)
	s2.friction = 1

	space.add(b2, s2)



def car(space: pymunk.Space) -> tuple[pymunk.Body, pymunk.Body, pymunk.Body]:
	pos = Vec2d(400, 100)

	SCALE = 2

	CHASSI_WIDTH = 60 * SCALE
	CHASSI_HEIGHT = 30 * SCALE

	AXLE_LENGTH = 30 * SCALE
	AXLE_RADIUS = 3 * SCALE
	AXLE_ANGLE = 40

	WHEEL_RADIUS = 15 * SCALE


	size = (CHASSI_WIDTH, CHASSI_HEIGHT)
	mass = 100
	moment = pymunk.moment_for_box(mass, size)
	chassi_b = pymunk.Body(mass, moment)
	chassi_s = pymunk.Poly.create_box(chassi_b, size)
	chassi_s.friction = 0.5
	space.add(chassi_b, chassi_s)

	wheel1_b = pymunk.Body(100, pymunk.moment_for_circle(100, 20, WHEEL_RADIUS))
	wheel1_s = pymunk.Circle(wheel1_b, WHEEL_RADIUS)
	wheel1_s.friction = 1.5
	space.add(wheel1_b, wheel1_s)

	wheel2_b = pymunk.Body(100, pymunk.moment_for_circle(100, 20, WHEEL_RADIUS))
	wheel2_s = pymunk.Circle(wheel2_b, WHEEL_RADIUS)
	wheel2_s.friction = 1.5
	space.add(wheel2_b, wheel2_s)

	AXLE1_TANGENT = Vec2d(1, 0).rotated(radians(-AXLE_ANGLE))

	AXLE1_P1, AXLE1_P2 = -AXLE_LENGTH / 2 * AXLE1_TANGENT, AXLE_LENGTH / 2 * AXLE1_TANGENT
	mass = 10
	moment = pymunk.moment_for_segment(10, AXLE1_P1, AXLE1_P2, AXLE_RADIUS)
	axle1_b = pymunk.Body(mass, moment)
	axle1_s = pymunk.Segment(axle1_b, AXLE1_P1, AXLE1_P2, AXLE_RADIUS)
	axle1_s.friction = 1.5
	space.add(axle1_b, axle1_s)

	AXLE2_TANGENT = Vec2d(1, 0).rotated(radians(AXLE_ANGLE))

	AXLE2_P1, AXLE2_P2 = -AXLE_LENGTH / 2 * AXLE2_TANGENT, AXLE_LENGTH / 2 * AXLE2_TANGENT
	mass = 10
	moment = pymunk.moment_for_segment(10, AXLE2_P1, AXLE2_P2, AXLE_RADIUS)
	axle2_b = pymunk.Body(mass, moment)
	axle2_s = pymunk.Segment(axle2_b, AXLE2_P1, AXLE2_P2, AXLE_RADIUS)
	axle2_s.friction = 1.5
	space.add(axle2_b, axle2_s)

	chassi_b.position = pos
	axle1_b.position = pos + (
		-(CHASSI_WIDTH / 2 - AXLE_RADIUS) - AXLE1_P2.x,
		CHASSI_HEIGHT / 2 - AXLE1_P2.y - AXLE_RADIUS
	)
	axle2_b.position = pos + (
		CHASSI_WIDTH / 2 - AXLE2_P1.x - AXLE_RADIUS,
		CHASSI_HEIGHT / 2 - AXLE2_P1.y - AXLE_RADIUS
	)

	wheel1_b.position = axle1_b.position + AXLE1_P1
	wheel2_b.position = axle2_b.position + AXLE2_P2

	j1 = pymunk.PivotJoint(chassi_b, axle1_b,
		(-(CHASSI_WIDTH / 2 - AXLE_RADIUS), CHASSI_HEIGHT / 2 - AXLE_RADIUS),
		AXLE1_P2
	)
	j1.collide_bodies = False
	s1 = pymunk.DampedRotarySpring(chassi_b, axle1_b, 0, 100000000, 900)
	space.add(j1, s1)

	j2 = pymunk.PivotJoint(chassi_b, axle2_b,
		(CHASSI_WIDTH / 2 - AXLE_RADIUS, CHASSI_HEIGHT / 2 - AXLE_RADIUS),
		AXLE2_P1
	)
	j2.collide_bodies = False
	s2 = pymunk.DampedRotarySpring(chassi_b, axle2_b, 0, 100000000, 900)
	space.add(j2, s2)

	j3 = pymunk.PivotJoint(axle1_b, wheel1_b, AXLE1_P1, (0, 0))
	j3.collide_bodies = False
	space.add(j3)
	j4 = pymunk.PivotJoint(axle2_b, wheel2_b, AXLE2_P2, (0, 0))
	j4.collide_bodies = False
	space.add(j4)

	return chassi_b, wheel1_b, wheel2_b


class PhysicsTestScene(IScene):
	def __init__(self):
		self._space = pymunk.Space()
		self._space.gravity = 0, 900

		floor(self._space)
		self._car = car(self._space)

		self._motor1 = pymunk.SimpleMotor(self._car[0], self._car[1], 0)
		self._motor1.max_force = 10000000
		self._motor2 = pymunk.SimpleMotor(self._car[0], self._car[2], 0)
		self._motor2.max_force = 10000000
		self._driving = False

	@override
	def on_enter(self) -> None:
		pass

	@override
	def on_exit(self) -> None:
		pass

	@override
	def handle_event(self, event: pygame.event.Event) -> None:
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_a and not self._driving:
				self._motor1.rate = 20
				self._motor2.rate = 20
				self._driving = True
				self._space.add(self._motor1, self._motor2)
			if event.key == pygame.K_d and not self._driving:
				self._motor1.rate = -20
				self._motor2.rate = -20
				self._driving = True
				self._space.add(self._motor1, self._motor2)
		if event.type == pygame.KEYUP:
			if (event.key == pygame.K_a or event.key == pygame.K_d) and self._driving:
				self._motor1.rate = 0
				self._motor2.rate = 0
				self._driving = False
				self._space.remove(self._motor1, self._motor2)

	@override
	def update(self, dt: float) -> None:
		self._space.step(dt)

	@override
	def render(self, screen: pygame.Surface) -> None:
		screen.fill(pygame.Color("white"))
		draw_options = pymunk.pygame_util.DrawOptions(screen)
		self._space.debug_draw(draw_options)
		pygame.display.flip()

	@override
	@classmethod
	def get_name(cls) -> str:
		return "test"