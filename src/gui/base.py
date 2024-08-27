from __future__ import annotations
import pygame
from abc import ABC, abstractmethod
from .style import Style, DEFAULT_STYLE
from core import app_state
from typing import Optional


class IElement(ABC):
	def __init__(self, *, left: Optional[int] = None, right: Optional[int] = None, top: Optional[int] = None, bottom: Optional[int] = None, style: Style = Style()):
		self.set_position(
			left=left,
			right=right,
			top=top,
			bottom=bottom
		)
		self._style = style
		self._parent: IContainer = None
		self._modifier: ISingleModifier = None

	def _get_parent_width(self) -> int:
		if self._parent:
			return self._parent.get_independent_size()[0]
		return app_state.width
	
	def _get_parent_height(self) -> int:
		if self._parent:
			return self._parent.get_independent_size()[1]
		return app_state.height

	def _get_left(self) -> int:
		if self._left is not None:
			return self._left
		if self._right is not None:
			return self._get_parent_width() - self.get_size()[0] - self._right
		return 0
	
	def _get_top(self) -> int:
		if self._top is not None:
			return self._top
		if self._bottom is not None:
			return self._get_parent_height() - self.get_size()[1] - self._bottom
		return 0

	def _get_independent_left(self) -> int:
		return (self._left or 0)
	
	def _get_independent_top(self) -> int:
		return (self._top or 0)

	def get_position(self) -> tuple[int, int]:
		pos = (self._get_left(), self._get_top())
		if self._modifier:
			offset_x, offset_y = self._modifier.get_offset()
			pos = (pos[0] + (offset_x or 0), pos[1] + (offset_y or 0))
		if self._parent:
			parent_pos = self._parent.get_position()
			pos = (pos[0] + parent_pos[0], pos[1] + parent_pos[1])
		return pos
	
	def get_independent_position(self) -> tuple[int, int]:
		pos = (self._get_independent_left(), self._get_independent_top())
		if self._modifier:
			offset = self._modifier.get_offset()
			pos = (pos[0] + offset[0], pos[1] + offset[1])
		return pos
	
	def set_position(self, *, left: Optional[int] = None, right: Optional[int] = None, top: Optional[int] = None, bottom: Optional[int] = None) -> None:
		self._left = left
		self._right = right
		self._top = top
		self._bottom = bottom

	def set_modifier(self, modifier: ISingleModifier) -> None:
		self._modifier = modifier
	
	def get_modifier(self) -> ISingleModifier:
		return self._modifier

	def set_parent(self, parent: IContainer) -> None:
		self._parent = parent

	def get_parent(self) -> IContainer:
		return self._parent

	def update_style(self, new_style: Style) -> None:
		self._style = self._style.update(new_style)

	def get_style(self) -> Style:
		style = DEFAULT_STYLE.parent_update(self._parent.get_style() if self._parent else Style()).update(self._style)
		if self._modifier:
			style = style.update(self._modifier.get_style_mod())
		return style

	def get_size(self) -> tuple[int, int]:
		width = height = 0
		style = self.get_style()
		width += style.padding_x * 2
		height += style.padding_y * 2
		if self._modifier:
			size_modifier = self._modifier.get_size_mod(self)
			width += size_modifier[0]
			height += size_modifier[1]
		return width, height

	def update(self, dt: float) -> None: ...

	def _draw_rect_with_aplha(self, screen: pygame.Surface, color: tuple[int, int, int, int], rect: tuple[int, int, int, int], border_width: int,  border_radius: int) -> None:
		# TODO: cache the surface
		x, y, width, height = rect
		alpha_surface = pygame.Surface((width, height), pygame.SRCALPHA)
		pygame.draw.rect(alpha_surface, color, alpha_surface.get_rect(), border_width, border_radius=border_radius)
		screen.blit(alpha_surface, (x, y))

	def render(self, screen: pygame.Surface) -> None:
		style = self.get_style()
		pos = self.get_position()

		if style.background_opacity > 0.01:
			bg_color = (style.background_color[0], style.background_color[1], style.background_color[2], 255 * style.background_opacity)

			self._draw_rect_with_aplha(
				screen,
				bg_color,
				(*pos, *self.get_size()),
				0,
				border_radius=style.border_radius
			)

		if style.border_opacity > 0.01 and style.border_width > 0:
			border_color = (style.border_color[0], style.border_color[1], style.border_color[2], 255 * style.border_opacity)
			self._draw_rect_with_aplha(
				screen,
				border_color,
				(*pos, *self.get_size()),
				style.border_width,
				border_radius=style.border_radius
			)

class IModifier(ABC):
	def get_offset(self) -> tuple[int, int]:
		return 0, 0

	def get_style_mod(self) -> Style:
		return Style()

	def get_size_mod(self, element: IElement) -> tuple[int, int]:
		return 0, 0


class ISingleModifier(IElement, IModifier):
	def __init__(self, target: IElement):
		self._target: IElement = target
		target.set_modifier(self)
		self._modifier: IModifier = None
	
	def get_position(self) -> tuple[int, int]:
		return self._target.get_position()
	
	def get_independent_position(self) -> tuple[int, int]:
		return self._target.get_independent_position()

	def set_position(self, *, left: Optional[int] = None, right: Optional[int] = None, top: Optional[int] = None, bottom: Optional[int] = None) -> None:
		self._target.set_position(
			left=left,
			right=right,
			top=top,
			bottom=bottom
		)
	
	def get_style(self) -> Style:
		return self._target.get_style()
	
	def update_style(self, new_style: Style) -> None:
		self._target.update_style(new_style)
		
	def get_parent(self) -> IContainer:
		return self._target.get_parent()
	
	def set_parent(self, parent: IContainer) -> None:
		self._target.set_parent(parent)
	
	def get_size(self) -> tuple[int, int]:
		return self._target.get_size()
	
	def get_size(self) -> tuple[int, int]:
		return self._target.get_size()
	
	def update(self, dt: float) -> None:
		self._target.update(dt)
	
	def render(self, screen: pygame.Surface) -> None:
		self._target.render(screen)
		
	def get_target(self) -> IElement:
		return self._target
	
	def get_offset(self) -> tuple[int, int]:
		if self._modifier:
			return self._modifier.get_offset()
		return 0, 0

	def get_style_mod(self) -> Style:
		if self._modifier:
			return self._modifier.get_style_mod()
		return Style()

	def get_size_mod(self, element: IElement) -> tuple[int, int]:
		if self._modifier:
			return self._modifier.get_size_mod(element)
		return 0, 0
	
	def set_modifier(self, modifier: IModifier) -> None:
		self._modifier = modifier
	
	def get_modifier(self) -> IModifier:
		return self._modifier



class IContainer(IElement):
	def __init__(self, *, left: Optional[int] = None, right: Optional[int] = None, top: Optional[int] = None, bottom: Optional[int] = None, style: Style = Style()):
		super().__init__(
			left=left,
			right=right,
			top=top,
			bottom=bottom,
			style=style
		)
		self._children: list[IElement] = []

	def add_child(self, child: IElement) -> None:
		if child.get_parent() is not None:
			child.get_parent().remove_child(child)
		self._children.append(child)
		child.set_parent(self)

	def with_children(self, *children: IElement) -> IContainer:
		for child in children:
			self.add_child(child)
		return self

	def remove_child(self, child: IElement) -> None:
		self._children.remove(child)
		child.set_parent(None)

	def get_children(self) -> list[IElement]:
		return self._children
	
	def get_independent_size(self) -> tuple[int, int]: ...