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

	wheel_color = 52, 219, 119, 255
	axle_color = 219, 119, 52, 255
	mass = 100
	radius = 25
	moment = pymunk.moment_for_circle(mass, 20, radius)
	wheel1_b = pymunk.Body(mass, moment)
	wheel1_s = pymunk.Circle(wheel1_b, radius)
	wheel1_s.friction = 1.5
	wheel1_s.color = wheel_color
	space.add(wheel1_b, wheel1_s)

	mass = 100
	radius = 25
	moment = pymunk.moment_for_circle(mass, 20, radius)
	wheel2_b = pymunk.Body(mass, moment)
	wheel2_s = pymunk.Circle(wheel2_b, radius)
	wheel2_s.friction = 1.5
	wheel2_s.color = wheel_color
	space.add(wheel2_b, wheel2_s)
	
	mass = 100
	size = (50, 30)
	moment = pymunk.moment_for_box(mass, size)
	chassi_b = pymunk.Body(mass, moment)
	chassi_s = pymunk.Poly.create_box(chassi_b, size)
	space.add(chassi_b, chassi_s)

	# vs = [(0, 0), (25, 45), (0, 45)]
	# shovel_s = pymunk.Poly(chassi_b, vs, transform=pymunk.Transform(tx=85))
	# shovel_s.friction = 0.5
	# shovel_s.color = shovel_color
	# space.add(shovel_s)

	wheel1_b.position = pos - (55, 0)
	wheel2_b.position = pos + (55, 0)
	chassi_b.position = pos + (0, -25)


	dist1 = wheel1_b.position.get_distance(chassi_b.position + (-25, -15))
	dist2 = wheel2_b.position.get_distance(chassi_b.position + (25, -15))

	mass = 10
	axle1_p1, axle1_p2 = wheel1_b.position, chassi_b.position + (-25, 15)
	moment = pymunk.moment_for_segment(mass, axle1_p1, axle1_p2, 2)
	axle1_b = pymunk.Body(mass, moment)
	axle1_s = pymunk.Segment(axle1_b, axle1_p1, axle1_p2, 2)
	axle1_s.friction = 1.5
	axle1_s.color = axle_color
	space.add(axle1_b, axle1_s)

	mass = 10
	axle2_p1, axle2_p2 = wheel2_b.position, chassi_b.position + (25, 15)
	moment = pymunk.moment_for_segment(mass, axle2_p1, axle2_p2, 2)
	axle2_b = pymunk.Body(mass, moment)
	axle2_s = pymunk.Segment(axle2_b, axle2_p1, axle2_p2, 2)
	axle2_s.friction = 1.5
	axle2_s.color = axle_color
	space.add(axle2_b, axle2_s)



	space.add(
		#pymunk.DampedSpring(wheel1_b, chassi_b, (0, 0), (-25, -15), dist1, 100000, 10),
		pymunk.PinJoint(wheel1_b, axle1_b, (0, 0), wheel1_b.position),
		pymunk.PinJoint(chassi_b, axle1_b, (-25, 15), chassi_b.position),
		#pymunk.RotaryLimitJoint(chassi_b, axle1_b, -0.5, 0.5),

		#pymunk.DampedSpring(wheel2_b, chassi_b, (0, 0), (25, -15), dist2, 100000, 10),
		pymunk.PinJoint(wheel2_b, axle2_b, (0, 0), wheel2_b.position),
		pymunk.PinJoint(chassi_b, axle2_b, (25, 15), chassi_b.position),
		#pymunk.RotaryLimitJoint(chassi_b, axle2_b, -0.5, 0.5),
#		pymunk.DampedRotarySpring(wheel1_b, chassi_b, 45, 100000000.0, 10000),
	)

	return chassi_b, wheel1_b, wheel2_b


class PhysicsTestScene(IScene):
	def __init__(self):
		self._space = pymunk.Space()
		self._space.gravity = 0, 0

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