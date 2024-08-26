from __future__ import annotations
import pygame
from .scene import IScene
from .app_state import AppState
import util.language_manager as lm



class App:
	"""
	Represents an application.
	Args:
		app_state (AppState): The state of the application.
	Methods:
		set_scene(scene: IScene) -> None:
			Sets the current scene of the application.
	"""
	def __init__(self, app_state: AppState) -> None:
		pygame.init()
		pygame.mixer.init()
		lm.init()
		lm.set_language("en")

		self._state = app_state

		self._screen = pygame.display.set_mode((self._state.width, self._state.height))
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

	def run(self) -> None:
		"""
		Runs the app.
		Raises:
			ValueError: If no scene is set for the app.
		"""
		if not self._scene:
			raise ValueError("No scene set for the app")
		
		self._state._running = True

		while self._state._running:
			self._handle_events()

			dt = self._clock.tick(60) / 1000
			self._update(dt)
			self._render()

	def _handle_events(self) -> None:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self._state._running = False
				return

			self._scene.handle_event(event)
			
	def _update(self, dt: float) -> None:
		self._scene.update(dt)

		if self._state._next_scene:
			self.set_scene(self._state._next_scene)
			self._state._next_scene = None

	def _render(self) -> None:
		self._scene.render(self._screen)
