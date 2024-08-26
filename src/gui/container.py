import pygame
from .base import IElement, IContainer
from .style import Style

class Container(IContainer):
	def __init__(self, /, pos: tuple[int, int] = (0, 0), style: Style = Style()) -> None:
		super().__init__(pos, style)
	
	def add_child(self, child: IElement) -> None:
		super().add_child(child)
		child.set_position((
			child.get_position()[0] + self.get_position()[0],
			child.get_position()[1] + self.get_position()[1]
		))

	def update(self, dt: float) -> None:
		for child in self.get_children():
			child.update(dt)
	
	def render(self, screen: pygame.Surface) -> None:
		for child in self.get_children():
			child.render(screen)
	
	def set_position(self, pos: tuple[int, int]) -> None:
		super().set_position(pos)
		delta = (pos[0] - self.get_position()[0], pos[1] - self.get_position()[1])
		for child in self.get_children():
			child.set_position((
				child.get_position()[0] + delta[0],
				child.get_position()[1] + delta[1]
			))
	
	def get_size(self) -> tuple[int, int]:
		min_x, min_y, max_x, max_y = 0, 0, 0, 0
		for child in self.get_children():
			child_min_x, child_min_y = child.get_position()
			child_max_x, child_max_y = child.get_size()
			child_max_x += child_min_x
			child_max_y += child_min_y
			min_x = min(min_x, child_min_x)
			min_y = min(min_y, child_min_y)
			max_x = max(max_x, child_max_x)
			max_y = max(max_y, child_max_y)
		return max_x - min_x, max_y - min_y