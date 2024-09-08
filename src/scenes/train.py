from scenes.level.player import Player
from scenes.level.camera import Camera
from core import IScene, app_state
from typing import override
import pygame
import pymunk


class TrainScene(IScene):
	@override
	@classmethod
	def get_name(cls) -> str:
		return "training_scene"

	def __init__(self) -> None:
		self._planet_data = app_state.get_planet_data(2)
		self._player_data = app_state.get_player_data()

		self._space = pymunk.Space()

		self._player = Player(self._space, 20, 20, self._planet_data, self._player_data)

		self._camera = Camera(30, 0.1)
		self._camera.follow_object(self._player)

	def on_enter(self) -> None:
		pass

	def on_exit(self) -> None:
		pass

	def handle_event(self, event: pygame.event.Event) -> None:
		pass

	def update(self, dt: float) -> None:
		self._player.physics_update(dt)
		self._space.step(dt)
		self._camera.update(dt)

	def render(self, screen: pygame.Surface) -> None:
		screen.fill((0, 0, 0))

		self._player.render(screen, self._camera)

		pygame.display.flip()
