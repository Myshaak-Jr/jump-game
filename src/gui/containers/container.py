import pygame
from ..base import IContainer
from ..style import AnyStyle


class Container(IContainer):
	def __init__(self, width: float | str = "auto", height: float | str = "auto", *, left: float | None = None, right: float | None = None, top: float | None = None, bottom: float | None = None, style: AnyStyle | None = None) -> None:
		self.set_width(width)
		self.set_height(height)
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

	def set_width(self, width: float | str) -> None:
		self._width = width if isinstance(width, str) else float(width)

	def set_height(self, height: float | str) -> None:
		self._height = height if isinstance(height, str) else float(height)

	def get_size(self) -> tuple[float, float]:
		width, height = 0, 0

		if self._width == "auto":
			min_x, max_x = 0, 0
			for child in self.get_children():
				child_min_x, _ = child.get_position()
				child_max_x, _ = child.get_size()
				child_max_x += child_min_x
				min_x = min(min_x, child_min_x)
				max_x = max(max_x, child_max_x)
			width = max_x - min_x
		elif isinstance(self._width, float):
			width = self._width
		
		if self._height == "auto":
			min_y, max_y = 0, 0
			for child in self.get_children():
				_, child_min_y = child.get_position()
				_, child_max_y = child.get_size()
				child_max_y += child_min_y
				min_y = min(min_y, child_min_y)
				max_y = max(max_y, child_max_y)
			height = max_y - min_y
		elif isinstance(self._height, float):
			height = self._height
		
		super_size = super().get_size()

		return width + super_size[0], height + super_size[1]
	
	def get_independent_size(self) -> tuple[float, float]:
		width, height = 0, 0

		if self._width == "auto":
			min_x, max_x = 0, 0
			for child in self.get_children():
				child_min_x, _ = child.get_independent_position()
				child_max_x, _ = child.get_size()
				child_max_x += child_min_x
				min_x = min(min_x, child_min_x)
				max_x = max(max_x, child_max_x)
			width = max_x - min_x
		elif isinstance(self._width, float):
			width = self._width
		
		if self._height == "auto":
			min_y, max_y = 0, 0
			for child in self.get_children():
				_, child_min_y = child.get_independent_position()
				_, child_max_y = child.get_size()
				child_max_y += child_min_y
				min_y = min(min_y, child_min_y)
				max_y = max(max_y, child_max_y)
			height = max_y - min_y
		elif isinstance(self._height, float):
			height = self._height

		super_size = super().get_size()

		return width + super_size[0], height + super_size[1]

