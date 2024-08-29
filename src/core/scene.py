from __future__ import annotations
import pygame
from abc import ABC, abstractmethod


__all__ = ["IScene"]


class IScene(ABC):
	"""Base class for scenes."""
	@abstractmethod
	def handle_event(self, event: pygame.event.Event) -> None:
		"""Handles event."""
		pass

	@abstractmethod
	def update(self, dt: float) -> None:
		"""Update the scene."""
		pass

	@abstractmethod
	def render(self, screen: pygame.Surface) -> None:
		"""Render the scene."""
		pass

	@classmethod
	@abstractmethod
	def get_name(cls) -> str: ...

	@abstractmethod
	def on_enter(self) -> None: ...

	@abstractmethod
	def on_exit(self) -> None: pass