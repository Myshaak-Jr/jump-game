import pygame
from ..base import IElement


class HSeparatorElement(IElement):
	def __init__(self, width: float, color: tuple[int, int, int], *, left: float | None = None, right: float | None = None, top: float | None = None, bottom: float | None = None):
		super().__init__(
			left=left,
			right=right,
			top=top,
			bottom=bottom
		)
		self._width = width
		self._color = color
	
	def render(self, screen):
		super().render(screen)
		x, y = self.get_position()
		width, height = self.get_size()
		pygame.draw.line(screen, self._color, (x, y + height // 2), (x + width, y + height // 2), 3)
	
	def get_size(self):
		super_size = super().get_size()

		return self._width + super_size[0], 3 + super_size[1]

class VSeparatorElement(IElement):
	def __init__(self, height: int | float, color: tuple[int, int, int], *, left: [float] = None, right: [float] = None, top: [float] = None, bottom: [float] = None):
		super().__init__(
			left=left,
			right=right,
			top=top,
			bottom=bottom
		)
		self._height = height
		self._color = color
	
	def render(self, screen):
		super().render(screen)
		x, y = self.get_position()
		width, height = self.get_size()
		pygame.draw.line(screen, self._color, (x + width // 2, y), (x + width // 2, y + height), 3)
		
	def get_size(self):
		super_size = super().get_size()

		return 3 + super_size[0], self._height + super_size[1]
