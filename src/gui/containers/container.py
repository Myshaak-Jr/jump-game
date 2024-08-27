import pygame
from ..base import IElement, IContainer
from ..style import Style
from typing import Optional


class Container(IContainer):
	def __init__(self, width: int | str = "auto", height: int | str = "auto", *, left: Optional[int] = None, right: Optional[int] = None, top: Optional[int] = None, bottom: Optional[int] = None, style: Style = Style()) -> None:
		self._width = width
		self._height = height
		super().__init__(
			left=left,
			right=right,
			top=top,
			bottom=bottom,
			style=style
		)
	
	def update(self, dt: float) -> None:
		for child in self.get_children():
			child.update(dt)
	
	def render(self, screen: pygame.Surface) -> None:
		super().render(screen)
		for child in self.get_children():
			child.render(screen)

	def set_width(self, width: int | str) -> None:
		self._width = width

	def set_height(self, height: int | str) -> None:
		self._height = height	

	def get_size(self) -> tuple[int, int]:
		width, height = self._width, self._height

		if self._width == "auto":
			min_x, max_x = 0, 0
			for child in self.get_children():
				child_min_x, _ = child.get_position()
				child_max_x, _ = child.get_size()
				child_max_x += child_min_x
				min_x = min(min_x, child_min_x)
				max_x = max(max_x, child_max_x)
			width = max_x - min_x
		
		if self._height == "auto":
			min_y, max_y = 0, 0
			for child in self.get_children():
				_, child_min_y = child.get_position()
				_, child_max_y = child.get_size()
				child_max_y += child_min_y
				min_y = min(min_y, child_min_y)
				max_y = max(max_y, child_max_y)
			height = max_y - min_y
		
		super_size = super().get_size()

		return width + super_size[0], height + super_size[1]
	
	def get_independent_size(self) -> tuple[int, int]:
		width, height = self._width, self._height

		if self._width == "auto":
			min_x, max_x = 0, 0
			for child in self.get_children():
				child_min_x, _ = child.get_independent_position()
				child_max_x, _ = child.get_size()
				child_max_x += child_min_x
				min_x = min(min_x, child_min_x)
				max_x = max(max_x, child_max_x)
			width = max_x - min_x
		
		if self._height == "auto":
			min_y, max_y = 0, 0
			for child in self.get_children():
				_, child_min_y = child.get_independent_position()
				_, child_max_y = child.get_size()
				child_max_y += child_min_y
				min_y = min(min_y, child_min_y)
				max_y = max(max_y, child_max_y)
			height = max_y - min_y
		
		super_size = super().get_size()

		return width + super_size[0], height + super_size[1]

