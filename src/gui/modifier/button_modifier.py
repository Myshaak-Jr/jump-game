import pygame
from ..base import ISingleModifier, IElement
from ..style import Style
from typing import Optional


class ButtonModifier(ISingleModifier):
	def __init__(self, target: IElement, *, on_click: callable, left: Optional[int] = None, right: Optional[int] = None, top: Optional[int] = None, bottom: Optional[int] = None, style: Style = Style(), _style_hovered: Style = Style(), _style_pressed: Style = Style()):
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
		self._style_hovered = _style_hovered
		self._style_pressed = _style_pressed
		
	def update(self, dt: float) -> None:
		mouse_pos = pygame.mouse.get_pos()
		mouse_pressed = pygame.mouse.get_pressed()
		x, y = self.get_position()
		width, height = self.get_size()

		if x <= mouse_pos[0] <= x + width and y <= mouse_pos[1] <= y + height:
			self._hovered = True
			if mouse_pressed[0]:
				self._pressed = True
			else:
				if self._pressed:
					self._pressed = False
					self._on_click()
		else:
			self._hovered = False
			self._pressed = False
		
		super().update(dt)

	def get_style_mod(self) -> Style:
		style = Style()
		if self._pressed:
			style = style.update(self._style_pressed)
		elif self._hovered:
			style = style.update(self._style_hovered)
		if self._modifier:
			style = style.update(self._modifier.get_style_mod())
		return style