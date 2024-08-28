from __future__ import annotations
from collections.abc import Callable
import pygame
from ..base import ISingleModifier, IElement
from ..style import Style


DEFAULT_STYLE_HOVERED = Style(
	background_color=(0, 0, 0),
	background_opacity=0.1,
)

DEFAULT_STYLE_PRESSED = Style(
	background_color=(0, 0, 0),
	background_opacity=0.2,
)

class ButtonModifier(ISingleModifier):
	def __init__(self, target: IElement, *, on_click: Callable[[], None] | None = None, left: float | None = None, right: float | None = None, top: float | None = None, bottom: float | None = None, style: Style = Style(), style_hovered: Style = DEFAULT_STYLE_HOVERED, style_pressed: Style = DEFAULT_STYLE_PRESSED):
		super().__init__(target)
		self._on_click = on_click
		self._hovered = False
		self._pressed = False
		self.set_position(
			left=left,
			right=right,
			top=top,
			bottom=bottom
		)
		self.update_style(style)
		self._style_hovered = style_hovered
		self._style_pressed = style_pressed
		
	def update(self, dt: float) -> None:
		if IElement.pressed_element is not None and IElement.pressed_element != self: return

		mouse_pos = pygame.mouse.get_pos()
		mouse_pressed = pygame.mouse.get_pressed()
		x, y = self.get_position()
		width, height = self.get_size()


		if x <= mouse_pos[0] <= x + width and y <= mouse_pos[1] <= y + height:
			self._hovered = True
		else:
			self._hovered = False
		
		if self._hovered and mouse_pressed[0]:
			self._pressed = True
			IElement.pressed_element = self
		elif self._pressed and not mouse_pressed[0]:
			self._pressed = False
			IElement.pressed_element = None
			if self._hovered and self._on_click:
				self._on_click()

		super().update(dt)

	def get_style_mod(self) -> Style:
		style = Style()
		if self._pressed:
			style = style.updated(self._style_pressed)
		elif self._hovered:
			style = style.updated(self._style_hovered)
		if self._modifier:
			style = style.updated(self._modifier.get_style_mod())
		return style