import pygame
from ..base import IContainer, GUIElement
from ..style import AnyStyle
from enum import Enum


class Alignment(Enum):
	CENTER = 0
	START = 1
	END = 2

class Justification(Enum):
	START = 0
	END = 1
	CENTER = 2
	SPACE_BETWEEN = 3
	SPACE_AROUND = 4
	SPACE_EVENLY = 5

class Direction(Enum):
	ROW = 0
	COLUMN = 1


class FlexContainer(IContainer):
	def __init__(self,
			  min_width: float = 0,
			  min_height: float = 0, *, direction: Direction = Direction.ROW, align: Alignment = Alignment.CENTER, justify: Justification = Justification.START, gap: float = 0, left: float | None = None, right: float | None = None, top: float | None = None, bottom: float | None = None, style: AnyStyle | None = None):
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
		self._width = min_width
		self._height = min_height
		self._gap = gap

	def get_direction(self) -> Direction:
		return self._direction

	def set_direction(self, direction: Direction) -> None:
		self._direction = direction

	def get_alignment(self) -> Alignment:
		return self._align
	
	def set_alignment(self, alignment: Alignment) -> None:
		self._align = alignment

	def get_justification(self) -> Justification:
		return self._justify

	def set_justification(self, justification: Justification) -> None:
		self._justify = justification

	def get_gap(self) -> float:
		return self._gap

	def set_gap(self, min_gap: float) -> None:
		self._gap = min_gap

	def set_min_size(self, width: float, height: float) -> None:
		self._width = width
		self._height = height

	def get_min_size(self) -> tuple[float, float]:
		return self._width, self._height

	def _calc_children_width(self) -> float:
		if self._direction == Direction.ROW:
			return sum(child.get_size()[0] for child in self._children)
		else:
			return max(child.get_size()[0] for child in self._children)
		
	def _calc_children_height(self) -> float:
		if self._direction == Direction.ROW:
			return max(child.get_size()[1] for child in self._children)
		else:
			return sum(child.get_size()[1] for child in self._children)
	
	def _calc_min_content_width(self) -> float:
		children_width = self._calc_children_width()
		if self._direction == Direction.ROW:
			return children_width + self._gap * (len(self._children) - 1)
		else:
			return children_width
	
	def _calc_min_content_height(self) -> float:
		children_height = self._calc_children_height()
		if self._direction == Direction.ROW:
			return children_height
		else:
			return children_height + self._gap * (len(self._children) - 1)

	def _calc_children_size(self) -> tuple[float, float]:
		return self._calc_children_width(), self._calc_children_height()

	def _calc_min_content_size(self) -> tuple[float, float]:
		return self._calc_min_content_width(), self._calc_min_content_height()

	def _calc_child_cross_pos(self, cross_size: float, child_cross_size: float) -> float:
		if self._align == Alignment.CENTER:
			return (cross_size - child_cross_size) / 2
		elif self._align == Alignment.START:
			return 0
		elif self._align == Alignment.END:
			return cross_size - child_cross_size
		else:
			raise ValueError("Invalid alignment")

	def _set_child_position(self, child: GUIElement, main_pos: float, cross_pos: float) -> None:
		if self._direction == Direction.ROW:
			child.set_position(left=main_pos, top=cross_pos)
		else:
			child.set_position(left=cross_pos, top=main_pos)

	def _update_start(self) -> None:
		child_main_pos = 0
		_, cross_size = self._orient(self.get_size())

		for child in self._children:
			child_main_size, child_cross_size = self._orient(child.get_size())

			child_cross_pos = self._calc_child_cross_pos(cross_size, child_cross_size)
			self._set_child_position(child, child_main_pos, child_cross_pos)

			child_main_pos += child_main_size + self._gap

	def _update_end(self) -> None:
		main_size, cross_size = self._orient(self.get_size())
		child_main_pos = main_size - self._orient(self._calc_min_content_size())[0]

		for child in self._children:
			child_main_size, child_cross_size = self._orient(child.get_size())

			child_cross_pos = self._calc_child_cross_pos(cross_size, child_cross_size)
			self._set_child_position(child, child_main_pos, child_cross_pos)

			child_main_pos += child_main_size + self._gap

	def _update_center(self) -> None:
		main_size, cross_size = self._orient(self.get_size())
		child_main_pos = (main_size - self._orient(self._calc_min_content_size())[0]) // 2

		for child in self._children:
			child_main_size, child_cross_size = self._orient(child.get_size())

			child_cross_pos = self._calc_child_cross_pos(cross_size, child_cross_size)
			self._set_child_position(child, child_main_pos, child_cross_pos)

			child_main_pos += child_main_size + self._gap

	def _update_space_between(self) -> None:
		main_size, cross_size = self._orient(self.get_size())
		child_main_pos = 0

		gap = (main_size - self._orient(self._calc_children_size())[0]) / (len(self._children) - 1)

		for child in self._children:
			child_main_size, child_cross_size = self._orient(child.get_size())

			child_cross_pos = self._calc_child_cross_pos(cross_size, child_cross_size)
			self._set_child_position(child, child_main_pos, child_cross_pos)

			child_main_pos += child_main_size + gap
	
	def _update_space_around(self) -> None:
		main_size, cross_size = self._orient(self.get_size())
		gap = (main_size - self._orient(self._calc_children_size())[0]) / len(self._children)
		child_main_pos = gap / 2

		for child in self._children:
			child_main_size, child_cross_size = self._orient(child.get_size())

			child_cross_pos = self._calc_child_cross_pos(cross_size, child_cross_size)
			self._set_child_position(child, child_main_pos, child_cross_pos)

			child_main_pos += child_main_size + gap

	def _update_space_evenly(self) -> None:
		main_size, cross_size = self._orient(self.get_size())
		gap = (main_size - self._orient(self._calc_children_size())[0]) / (len(self._children) + 1)
		child_main_pos = gap

		for child in self._children:
			child_main_size, child_cross_size = self._orient(child.get_size())

			child_cross_pos = self._calc_child_cross_pos(cross_size, child_cross_size)
			self._set_child_position(child, int(child_main_pos), child_cross_pos)

			child_main_pos += child_main_size + gap


	def update(self, dt: float) -> None:

		if self._justify == Justification.START:
			self._update_start()
		elif self._justify == Justification.END:
			self._update_end()
		elif self._justify == Justification.CENTER:
			self._update_center()
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
	
	def _orient(self, vector: tuple[float, float]) -> tuple[float, float]:
		if self._direction == Direction.ROW:
			return vector
		else:
			return tuple[float, float](vector[::-1])

	def get_size(self) -> tuple[float, float]:
		width, height = super().get_size()

		content_width, content_height = self._calc_min_content_size()

		width += max(content_width, self._width)
		height += max(content_height, self._height)

		return width, height
	
	def get_independent_size(self) -> tuple[float, float]:
		return self._width, self._height
