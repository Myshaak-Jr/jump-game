from core import IScene, app_state
import pygame
from gui import Container, LabelElement, Style
from styles import LABEL_STYLE
import util.language_manager as lm


GRAVITY_BASE = 9.8 * 10
PLAYER_FORCE = 1000


class Player:
	def __init__(self, x: float, y: float) -> None:
		self.x = x
		self.y = y
		self.vel_x = 0
		self.vel_y = 0
		self.force_x = 0
		self.force_y = 0
		self.inv_mass = 1

	def apply_force(self, force_x: float, force_y: float) -> None:
		self.force_x += force_x
		self.force_y += force_y
	
	def update(self, dt: float) -> bool:
		self.vel_x += self.force_x * self.inv_mass * dt
		self.vel_y += self.force_y * self.inv_mass * dt

		self.x += self.vel_x * dt
		self.y += self.vel_y * dt

		self.force_x = 0
		self.force_y = 0

		if self.y > app_state.height - 10:
			return True
		
		return False
	
	def render(self, screen) -> None:
		pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), 10)


class LevelScene(IScene):
	name = "level"
	def __init__(self, planet) -> None:
		self.player_pos = Player(app_state.width // 4, app_state.height // 2)
		self.planet = planet
		self.gravity = app_state.get_planet_data(planet)["gravity"]

		self.gui = Container().with_children(
			LabelElement(lm.get(f"planet.{planet}.name"), style=LABEL_STYLE),
		)

		pygame.display.set_caption("Play")

	def handle_event(self, event: pygame.event.Event) -> None:
		pass

	def update(self, dt: float) -> None:
		key_state = pygame.key.get_pressed()
		if key_state[pygame.K_UP]:
			self.player_pos.apply_force(0, -PLAYER_FORCE)
		if key_state[pygame.K_DOWN]:
			self.player_pos.apply_force(0, PLAYER_FORCE)
		self.player_pos.apply_force(0, GRAVITY_BASE * self.gravity)

		died = self.player_pos.update(dt)
		if died:
			app_state.queue_scene("game_over", self.planet)
		
		self.gui.update(dt)

	def render(self, screen: pygame.Surface) -> None:
		screen.fill((0, 0, 0))

		self.player_pos.render(screen)

		self.gui.render(screen)

		pygame.display.flip()
