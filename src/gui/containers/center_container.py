import pygame
from ..base import IContainer
from ..style import Style
from typing import Optional


class HCenterContainer(IContainer):
	def __init__(self, width: int, gap: int = 0, *, left: Optional[int] = None, right: Optional[int] = None, top: Optional[int] = None, bottom: Optional[int] = None, style: Style = Style()):
		super().__init__(
			left=left,
			right=right,
			top=top,
			bottom=bottom,
			style=style
		)
		self._width = width
		self._gap = gap

	def update(self, dt: float) -> None:
		y = 0
		width = self.get_size()[0]

		for child in self._children:
			child_width, child_height = child.get_size()
			x = (width - child_width) // 2
			child.set_position(left=x, top=y)
			y += child_height + self._gap

			child.update(dt)

	def render(self, screen: pygame.Surface):
		super().render(screen)
		for child in self._children:
			child.render(screen)
	
	def get_size(self) -> tuple[int, int]:
		width, height = super().get_size()
		width += self._width
		height += sum(child.get_size()[1] for child in self._children) + self._gap * (len(self._children) - 1)
		return width, height
	
	def get_independent_size(self) -> tuple[int, int]:
		return self.get_size()

class VCenterContainer(IContainer):
	def __init__(self, height: int, gap: int = 0, *, left: Optional[int] = None, right: Optional[int] = None, top: Optional[int] = None, bottom: Optional[int] = None, style: Style = Style()):
		super().__init__(
			left=left,
			right=right,
			top=top,
			bottom=bottom,
			style=style
		)
		self._gap = gap
		self._height = height

	def update(self, dt: float) -> None:
		x = 0
		height = self.get_size()[1]

		for child in self._children:
			child_width, child_height = child.get_size()
			y = (height - child_height) // 2
			child.set_position(left=x, top=y)
			x += child_width + self._gap
			
			child.update(dt)

	def render(self, screen: pygame.Surface) -> None:
		super().render(screen)
		for child in self._children:
			child.render(screen)
	
	def get_size(self) -> tuple[int, int]:
		width, height = super().get_size()
		width += sum(child.get_size()[0] for child in self._children) + self._gap * (len(self._children) - 1)
		height += self._height
		return width, height

	def get_independent_size(self) -> tuple[int, int]:
		return self.get_size()