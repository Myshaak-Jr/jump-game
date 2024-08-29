from __future__ import annotations
import pygame
from abc import ABC
from .style import AnyStyle, FullStyle, DEFAULT_STYLE
from core import app_state
from typing import Self, overload
from collections.abc import Iterable
from util.draw import draw_rect_opacity


__all__ = [
	"GUIElement",
	"IModifier",
	"ISingleModifier",
	"IContainer"
]


class GUIElement:
	pressed_element: GUIElement | None = None

	def __init__(self, *, left: float | None = None, right: float | None = None, top: float | None = None, bottom: float | None = None, style: AnyStyle | None = None):
		self.set_position(
			left=left,
			right=right,
			top=top,
			bottom=bottom
		)
		self._style = style
		self._parent: IContainer | None = None
		self._modifier: IModifier | None = None

	def _get_parent_width(self) -> float:
		if self._parent:
			return self._parent.get_independent_size()[0]
		return app_state.get_width()
	
	def _get_parent_height(self) -> float:
		if self._parent:
			return self._parent.get_independent_size()[1]
		return app_state.get_height()

	def _get_left(self) -> float:
		if self._left is not None:
			return self._left
		if self._right is not None:
			return self._get_parent_width() - self.get_raw_size()[0] - self._right
		return 0
	
	def _get_top(self) -> float:
		if self._top is not None:
			return self._top
		if self._bottom is not None:
			return self._get_parent_height() - self.get_raw_size()[1] - self._bottom
		return 0

	def _get_independent_left(self) -> float:
		return (self._left or 0)
	
	def _get_independent_top(self) -> float:
		return (self._top or 0)

	def get_position(self) -> tuple[float, float]:
		pos = (self._get_left(), self._get_top())
		if self._modifier:
			offset_x, offset_y = self._modifier.get_offset()
			pos = (pos[0] + (offset_x or 0), pos[1] + (offset_y or 0))
		if self._parent:
			parent_pos = self._parent.get_position()
			pos = (pos[0] + parent_pos[0], pos[1] + parent_pos[1])
		return pos
	
	def get_independent_position(self) -> tuple[float, float]:
		pos = (self._get_independent_left(), self._get_independent_top())
		if self._modifier:
			offset = self._modifier.get_offset()
			pos = (pos[0] + offset[0], pos[1] + offset[1])
		return pos
	
	def set_position(self, *, left: float | None = None, right: float | None = None, top: float | None = None, bottom: float | None = None) -> None:
		self._left = float(left) if left is not None else None
		self._right = float(right) if right is not None else None
		self._top = float(top) if top is not None else None
		self._bottom = float(bottom) if bottom is not None else None

	def set_modifier(self, modifier: IModifier | None) -> None:
		self._modifier = modifier
	
	def get_modifier(self) -> IModifier | None:
		return self._modifier

	def set_parent(self, parent: IContainer | None) -> None:
		self._parent = parent

	def get_parent(self) -> IContainer | None:
		return self._parent

	def update_style(self, new_style: AnyStyle | None) -> None:
		if self._style:
			self._style = self._style.updated(new_style)
		else:
			self._style = new_style

	def get_style(self) -> FullStyle:
		style = DEFAULT_STYLE.parent_updated(self._parent.get_style() if self._parent else None).updated(self._style)
		if self._modifier:
			style = style.updated(self._modifier.get_style_mod())
		return style

	def get_size(self) -> tuple[float, float]:
		width = height = 0
		style = self.get_style()
		width += (style.padding_x or 0) * 2
		height += (style.padding_y or 0) * 2
		if self._modifier:
			size_modifier = self._modifier.get_size_mod(self)
			width += size_modifier[0]
			height += size_modifier[1]
		return width, height

	def get_raw_size(self) -> tuple[float, float]:
		return self.get_size()

	def update(self, dt: float) -> None: ...

	def render(self, screen: pygame.Surface) -> None:
		style = self.get_style()
		pos = self.get_position()

		if style.background_opacity > 0.01:
			draw_rect_opacity(
				screen,
				style.background_color,
				style.background_opacity,
				pygame.Rect(*pos, *self.get_size()),
				0,
				border_radius=style.border_radius
			)

		if style.border_opacity > 0.01 and style.border_width > 0:
			draw_rect_opacity(
				screen,
				style.border_color,
				style.border_opacity,
				pygame.Rect(*pos, *self.get_size()),
				style.border_width,
				border_radius=style.border_radius
			)

class IModifier(ABC):
	def get_offset(self) -> tuple[float, float]:
		return 0, 0

	def get_style_mod(self) -> AnyStyle | None:
		return None

	def get_size_mod(self, element: GUIElement) -> tuple[float, float]:
		return 0, 0


class ISingleModifier(GUIElement, IModifier):
	def __init__(self, target: GUIElement):
		self._target: GUIElement = target
		target.set_modifier(self)
		self._modifier: IModifier | None = None
	
	def get_position(self) -> tuple[float, float]:
		return self._target.get_position()
	
	def get_independent_position(self) -> tuple[float, float]:
		return self._target.get_independent_position()

	def set_position(self, *, left: float | None = None, right: float | None = None, top: float | None = None, bottom: float | None = None) -> None:
		self._target.set_position(
			left=left,
			right=right,
			top=top,
			bottom=bottom
		)
	
	def get_style(self) -> FullStyle:
		return self._target.get_style()
	
	def update_style(self, new_style: AnyStyle | None) -> None:
		self._target.update_style(new_style)
		
	def get_parent(self) -> IContainer | None:
		return self._target.get_parent()
	
	def set_parent(self, parent: IContainer | None) -> None:
		self._target.set_parent(parent)
		
	def get_size(self) -> tuple[float, float]:
		return self._target.get_size()
	
	def update(self, dt: float) -> None:
		self._target.update(dt)
	
	def render(self, screen: pygame.Surface) -> None:
		self._target.render(screen)
		
	def get_target(self) -> GUIElement:
		return self._target
	
	def get_offset(self) -> tuple[float, float]:
		if self._modifier:
			return self._modifier.get_offset()
		return 0, 0

	def get_style_mod(self) -> AnyStyle | None:
		if self._modifier:
			return self._modifier.get_style_mod()
		return None

	def get_size_mod(self, element: GUIElement) -> tuple[float, float]:
		if self._modifier:
			return self._modifier.get_size_mod(element)
		return 0, 0
	
	def set_modifier(self, modifier: IModifier | None) -> None:
		self._modifier = modifier
	
	def get_modifier(self) -> IModifier | None:
		return self._modifier

class IContainer(GUIElement):
	def __init__(self, *, left: float | None = None, right: float | None = None, top: float | None = None, bottom: float | None = None, style: AnyStyle | None = None):
		super().__init__(
			left=left,
			right=right,
			top=top,
			bottom=bottom,
			style=style
		)
		self._children: list[GUIElement] = []

	def add_child(self, child: GUIElement) -> None:
		parent = child.get_parent()
		if parent is not None:
			parent.remove_child(child)
		self._children.append(child)
		child.set_parent(self)

	@overload
	def with_children(self, children: Iterable[GUIElement]) -> Self: ...

	@overload
	def with_children(self, *children: GUIElement) -> Self: ...

	def with_children(self, children: Iterable[GUIElement], *rest: GUIElement) -> Self:
		if not rest and not isinstance(children, GUIElement):
			for child in list(children):
				self.add_child(child)
		elif isinstance(children, GUIElement):
			for child in [children, *rest]:
				self.add_child(child)
		return self

	def remove_child(self, child: GUIElement) -> None:
		self._children.remove(child)
		child.set_parent(None)

	def get_children(self) -> list[GUIElement]:
		return self._children
	
	def get_independent_size(self) -> tuple[float, float]: ...