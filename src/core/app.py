from __future__ import annotations
import pygame
from .scene import IScene
from .app_state import app_state
import util.language_manager as lm
import util.logger as log


class App:
	"""
	Represents an application.
	Args:
		app_state (AppState): The state of the application.
	Methods:
		set_scene(scene: IScene) -> None:
			Sets the current scene of the application.
	"""
	def __init__(self) -> None:
		log.info("Initializing the app...")
		pygame.init()
		pygame.mixer.init()
		lm.init()
		lm.set_language("en")

		self._screen = pygame.display.set_mode((app_state.width, app_state.height))
		self._clock = pygame.time.Clock()

		self._scene: IScene = None
	
	def set_scene(self, scene: IScene) -> None:
		"""
		Sets the current scene of the app.

		Parameters:
			scene (IScene): The scene to set as the current scene.

		Returns:
			None
		"""
		self._scene = scene
		log.info(f"Switching the scene to {scene.get_name()}")

	def run(self) -> None:
		"""
		Runs the app.
		Raises:
			ValueError: If no scene is set for the app.
		"""
		if not self._scene:
			raise ValueError("No scene set for the app")
		
		app_state._running = True

		while app_state._running:
			self._handle_events()

			dt = self._clock.tick(60) / 1000
			dt = min(dt, 1/30) # clamp the delta time to 1/30
			self._update(dt)
			self._render()

	def quit(self) -> None:
		"""Quits the application."""
		log.info("Exiting the app...")
		pygame.quit()
	
	def _handle_events(self) -> None:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				app_state._running = False
				return

			self._scene._handle_event(event)
			
	def _update(self, dt: float) -> None:
		self._scene.update(dt)

		if app_state._next_scene:
			self.set_scene(app_state._next_scene)
			app_state._next_scene = None
			self._scene.update(dt)

	def _render(self) -> None:
		self._scene.render(self._screen)
