import pygame
from .base import IContainer
from .style import Style


class HCenterContainer(IContainer):
	def __init__(self, width: int, gap: int = 0, /, pos: tuple[int, int] = (0, 0), style: Style = Style()):
		super().__init__(pos, style)
		self._width = width
		self._gap = gap

	def update(self, dt: float) -> None:
		y = 0
		for child in self._children:
			child_width, child_height = child.get_size()
			x = (self._width - child_width) // 2
			child.set_position((self._pos[0] + x, self._pos[1] + y))
			y += child_height + self._gap

			child.update(dt)
		
	def render(self, screen: pygame.Surface):
		super().render(screen)
		for child in self._children:
			child.render(screen)

	def get_size(self) -> tuple[int, int]:
		width = self._width
		height = sum(child.get_size()[1] for child in self._children) + self._gap * (len(self._children) - 1)
		style = self.get_style()
		width += style.padding_x * 2
		height += style.padding_y * 2
		return width, height

class VCenterContainer(IContainer):
	def __init__(self, height: int, gap: int = 0, /, pos: tuple[int, int] = (0, 0), style: Style = Style()):
		super().__init__(pos, style)
		self._gap = gap
		self._height = height

	def update(self, dt: float) -> None:
		x = 0
		for child in self._children:
			child_width, child_height = child.get_size()
			y = (self._height - child_height) // 2
			child.set_position((self._pos[0] + x, self._pos[1] + y))
			x += child_width + self._gap
			
			child.update(dt)

	def render(self, screen: pygame.Surface) -> None:
		super().render(screen)
		for child in self._children:
			child.render(screen)

	def get_size(self) -> tuple[int, int]:
		width = sum(child.get_size()[0] for child in self._children) + self._gap * (len(self._children) - 1)
		height = self._height
		style = self.get_style()
		width += style.padding_x * 2
		height += style.padding_y * 2
		return width, height