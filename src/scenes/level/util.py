from abc import ABC, abstractmethod
from typing import override
import pygame

from util.my_math import Vec2


__all__ = [
	"IHasRect",
	"GLOBAL_SCALE"
]


GLOBAL_SCALE = 3.0

class IHasPos(ABC):
	@abstractmethod
	def get_pos(self) -> Vec2: ...

class IHasRect(IHasPos):
	@abstractmethod
	def get_rect(self) -> pygame.FRect: ...

	@override
	def get_pos(self) -> Vec2:
		rect = self.get_rect()
		return Vec2(rect.center)