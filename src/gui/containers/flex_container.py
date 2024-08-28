import pygame
from ..base import IContainer
from ..style import Style
from typing import Optional
from enum import Enum


class Alignment(Enum):
	CENTER = 0
	START = 1
	END = 2

class Justification(Enum):
	START = 0
	END = 1
	SPACE_AROUND = 2
	SPACE_BETWEEN = 3
	SPACE_EVENLY = 4

class Direction(Enum):
	ROW = 0
	COLUMN = 1


class FlexContainer(IContainer):
	def __init__(self, width: int, height: int, *,
		direction: Direction = Direction.ROW,
		align: Alignment = Alignment.CENTER,
		justify: Justification = Justification.START,
		min_gap: int = 0,
		left: Optional[int] = None,
		right: Optional[int] = None,
		top: Optional[int] = None,
		bottom: Optional[int] = None,
		style: Style = Style()):
		super().__init__(
			left=left,
			right=right,
			top=top,
			bottom=bottom,
			style=style
		)
		self._direction = direction
		self._align = align
		self._justify = justify
		self._width = width
		self._height = height
		self._min_gap = min_gap

	def _calc_child_cross_pos(self, cross_size: int, child_cross_size: int) -> int:
		if self._align == Alignment.CENTER:
			return (cross_size - child_cross_size) // 2
		elif self._align == Alignment.START:
			return 0
		elif self._align == Alignment.END:
			return cross_size - child_cross_size

	def _update_start(self) -> None:
		main_pos = 0
		main_size, cross_size = self._orient(self.get_size())
		children_main_size = self._calc_children_main_size()

		for child in self._children:
			child_main_size, child_cross_size = self._orient(child.get_size())

			child_cross_pos = self._calc_child_cross_pos(main_size, child_main_size)


	def update(self, dt: float) -> None:

		if self._justify == Justification.START:
			self._update_start()
		elif self._justify == Justification.END:
			self._update_end()
		elif self._justify == Justification.SPACE_AROUND:
			self._update_space_around()
		elif self._justify == Justification.SPACE_BETWEEN:
			self._update_space_between()
		elif self._justify == Justification.SPACE_EVENLY:
			self._update_space_evenly()

		for child in self._children:
			child.update(dt)

	def render(self, screen: pygame.Surface):
		super().render(screen)
		for child in self._children:
			child.render(screen)
	
	def _orient(self, vector: tuple[int, int]) -> tuple[int, int]:
		if self._direction == Direction.ROW:
			return vector
		else:
			return vector[::-1]

	def _calc_children_main_size(self) -> int:
		return sum(self._orient(child.get_size())[0] for child in self._children) + self._min_gap * (len(self._children) - 1)

	def get_size(self) -> tuple[int, int]:
		width, height = super().get_size()

		if self._direction == Direction.ROW:
			width += max(self._calc_children_main_size(), self._width)
			height += self._height
		else:
			width += self._width
			height += max(self._calc_children_main_size(), self._height)

		return width, height
	
	def get_independent_size(self) -> tuple[int, int]:
		return self.get_size()




class ColumnContainer(IContainer):
	def __init__(self, width: int, height: int = 0, *, align: Alignment = Alignment.CENTER, justify: Justification = Justification.START, min_gap: int = 0, left: Optional[int] = None, right: Optional[int] = None, top: Optional[int] = None, bottom: Optional[int] = None, style: Style = Style()):
		super().__init__(
			left=left,
			right=right,
			top=top,
			bottom=bottom,
			style=style
		)
		self._align = align
		self._width = width
		self._height = height
		self._min_gap = min_gap


	def _get_new_x(self, width: int) -> int:
		if self._align == Alignment.CENTER:
			return (self._width - width) // 2
		elif self._align == Alignment.START:
			return 0
		elif self._align == Alignment.END:
			return self._width - width

	def update(self, dt: float) -> None:
		y = 0
		width, height = self.get_size()

		for child in self._children:
			child_width, child_height = child.get_size()

			if self._align == Alignment.CENTER:
				x = (width - child_width) // 2
				child.set_position(left=x, top=y)
			elif self._align == Alignment.START:
				child.set_position(left=0, top=y)
			elif self._align == Alignment.END:
				child.set_position(right=0, top=y)

			y += child_height + self._min_gap

			child.update(dt)

	def render(self, screen: pygame.Surface):
		super().render(screen)
		for child in self._children:
			child.render(screen)
	
	def get_size(self) -> tuple[int, int]:
		width, height = super().get_size()
		width += self._width
		my_height = sum(child.get_size()[1] for child in self._children) + self._min_gap * (len(self._children) - 1)
		height += max(my_height, self._height)
		return width, height
	
	def get_independent_size(self) -> tuple[int, int]:
		return self.get_size()


class RowContainer(IContainer):
	def __init__(self, height: int, *, align: Alignment = Alignment.CENTER, gap: int = 0, left: Optional[int] = None, right: Optional[int] = None, top: Optional[int] = None, bottom: Optional[int] = None, style: Style = Style()):
		super().__init__(
			left=left,
			right=right,
			top=top,
			bottom=bottom,
			style=style
		)
		self._align = align
		self._gap = gap
		self._height = height

	def update(self, dt: float) -> None:
		x = 0
		height = self.get_size()[1]

		for child in self._children:
			child_width, child_height = child.get_size()

			if self._align == Alignment.CENTER:
				y = (height - child_height) // 2
				child.set_position(left=x, top=y)
			elif self._align == Alignment.START:
				child.set_position(left=x, top=0)
			elif self._align == Alignment.END:
				child.set_position(left=x, bottom=0)

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