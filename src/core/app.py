from __future__ import annotations
import pygame
from .scene import IScene
from . import app_state
import util.language_manager as lm
import util.logger as log
from typing import Any, overload
from .structs import NewSceneData


__all__ = ["App"]


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

		self._screen = pygame.display.set_mode((app_state.get_width(), app_state.get_height()))
		self._clock = pygame.time.Clock()

		self._scene: IScene | None = None

		app_state.register_resolution_changed_callback(self._on_resolution_changed)
	
	def _on_resolution_changed(self, width: int, height: int) -> None:
		self._screen = pygame.display.set_mode((width, height))

	@overload
	def set_scene(self, scene: IScene) -> None: ...

	@overload
	def set_scene(self, scene: str, *args: Any, **kwargs: Any) -> None: ...

	@overload
	def set_scene(self, scene: NewSceneData) -> None: ...

	def set_scene(self, scene: NewSceneData | IScene | str | None, *args: Any, **kwargs: Any) -> None:
		"""
		Sets the current scene of the app.

		Parameters:
			scene (IScene): The scene to set as the current scene.

		Returns:
			None
		"""

	

		if scene is None:
			raise ValueError("Scene cannot be None")

		if self._scene:
			self._scene.on_exit()
		
		if isinstance(scene, IScene):
			self._scene = scene
			log.info(f"Switching back to scene '{scene.get_name()}'")
		elif isinstance(scene, str):
			if not app_state.has_scene(scene):
				raise ValueError(f"Attemped to queue unknown scene {scene}")
			self._scene = app_state.get_scene(scene)(*args, **kwargs)
			log.info(f"Switching to a new scene '{scene}'")
		else:
			if not app_state.has_scene(scene.name):
				raise ValueError(f"Attemped to queue unknown scene {scene.name}")
			self._scene = app_state.get_scene(scene.name)(*scene.args, **scene.kwargs)
			log.info(f"Switching to a new scene '{scene.name}'")
		
		self._scene.on_enter()
		
	@overload
	def run(self, scene: None) -> None: ...

	@overload
	def run(self, scene: str, *args: Any, **kwargs: Any) -> None: ...
	
	@overload
	def run(self, scene: IScene) -> None: ...
	
	@overload
	def run(self, scene: NewSceneData) -> None: ...

	def run(self, scene: str | IScene | NewSceneData | None, *args: Any, **kwargs: Any) -> None:
		"""
		Runs the app.
		Raises:
			ValueError: If no scene is set for the app.
		"""
		if scene:
			self.set_scene(scene, *args, **kwargs)
		
		if not self._scene:
			raise ValueError("No scene set for the app")
		
		app_state.start()

		while app_state.is_running():
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
				app_state.queue_stop()
				return

			if self._scene:
				self._scene.handle_event(event)
			
	def _update(self, dt: float) -> None:
		if self._scene:
			self._scene.update(dt)

		next_scene = app_state.get_next_scene()
		if next_scene is not None:
			self.set_scene(next_scene)
			app_state.clear_next_scene()
			if self._scene:
				self._scene.update(dt)

	def _render(self) -> None:
		if self._scene:
			self._scene.render(self._screen)
