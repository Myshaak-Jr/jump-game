from __future__ import annotations
import pygame
from abc import ABC, abstractmethod
from .style import Style, DEFAULT_STYLE


class IElement(ABC):
	def __init__(self, /, pos: tuple[int, int] = (0, 0), style: Style = Style()):
		self._pos = pos
		self._style = style
		self._parent: IContainer = None
		self._modifier: IModifier = None

	def get_position(self) -> tuple[int, int]:
		pos = self._pos
		if self._modifier:
			offset = self._modifier.get_offset()
			pos = (pos[0] + offset[0], pos[1] + offset[1])
		return pos

	def set_position(self, pos: tuple[int, int]) -> None:
		self._pos = pos

	def set_modifier(self, modifier: IModifier) -> None:
		self._modifier = modifier
	
	def get_modifier(self) -> IModifier:
		return self._modifier

	def set_parent(self, parent: IContainer) -> None:
		self._parent = parent

	def get_parent(self) -> IContainer:
		return self._parent

	def update_style(self, new_style: Style) -> None:
		self._style = self._style.update(new_style)

	def get_style(self) -> Style:
		style = (self._parent.get_style() if self._parent else DEFAULT_STYLE).update(self._style)
		if self._modifier:
			style = style.update(self._modifier.get_style_mod())
		return style

	@abstractmethod
	def get_size(self) -> tuple[int, int]: ...

	def update(self, dt: float) -> None: ...

	def _draw_rect_with_aplha(self, screen: pygame.Surface, color: tuple[int, int, int, int], rect: tuple[int, int, int, int], border_width: int,  border_radius: int) -> None:
		# TODO: cache the surface
		x, y, width, height = rect
		alpha_surface = pygame.Surface((width, height), pygame.SRCALPHA)
		pygame.draw.rect(alpha_surface, color, alpha_surface.get_rect(), border_width, border_radius=border_radius)
		screen.blit(alpha_surface, (x, y))

	def render(self, screen: pygame.Surface) -> None:
		style = self.get_style()

		if style.background_opacity > 0.01:
			bg_color = (style.background_color[0], style.background_color[1], style.background_color[2], 255 * style.background_opacity)

			self._draw_rect_with_aplha(
				screen,
				bg_color,
				(*self.get_position(), *self.get_size()),
				0,
				border_radius=style.border_radius
			)

		if style.border_opacity > 0.01 and style.border_width > 0:
			border_color = (style.border_color[0], style.border_color[1], style.border_color[2], 255 * style.border_opacity)
			self._draw_rect_with_aplha(
				screen,
				border_color,
				(*self.get_position(), *self.get_size()),
				style.border_width,
				border_radius=style.border_radius
			)

class IModifier(IElement):
	def __init__(self, target: IElement):
		self._target: IElement = target
		target.set_modifier(self)
	
	def get_position(self) -> tuple[int, int]:
		return self._target.get_position()
	
	def set_position(self, pos: tuple[int, int]) -> None:
		self._target.set_position(pos)
	
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
	
	def update(self, dt: float) -> None:
		self._target.update(dt)
	
	def render(self, screen: pygame.Surface) -> None:
		self._target.render(screen)
	
	def set_modifier(self, modifier: IModifier) -> None:
		raise ValueError("Cannot set modifier to a modifier")
	
	def get_modifier(self) -> IModifier:
		return self
	
	def get_target(self) -> IElement:
		return self._target
	
	@abstractmethod
	def get_offset(self) -> tuple[int, int]: ...

	@abstractmethod
	def get_style_mod(self) -> Style: ...

class IContainer(IElement):
	def __init__(self, /, pos: tuple[int, int] = (0, 0), style: Style = Style()):
		super().__init__(pos, style)
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
