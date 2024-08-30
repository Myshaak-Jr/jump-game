from abc import ABC, abstractmethod
import pygame


__all__ = [
	"IHasRect",
	"GLOBAL_SCALE"
]


GLOBAL_SCALE = 3.0


class IHasRect(ABC):
	@abstractmethod
	def get_rect(self) -> pygame.FRect: ...