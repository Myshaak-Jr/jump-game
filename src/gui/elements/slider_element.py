import pygame
from ..base import IElement
from typing import Callable
from util.draw import draw_rect_opacity, draw_circle_opacity


class SliderElement(IElement):
	def __init__(self, width, *, min: float, max: float, default: float, step: float, on_change: Callable[[float], None], left: int = None, right: int = None, top: int = None, bottom: int = None):
		super().__init__(
			left=left,
			right=right,
			top=top,
			bottom=bottom
		)
		self._width = width
		self._min = min
		self._max = max
		self._value = default
		self._step = step
		self._on_change = on_change
	
		self._dir = 1

	def update(self, dt):
		SPEED = 20

		self._value += self._dir * SPEED * dt

		if self._value < self._min:
			self._value = self._min
			self._dir = 1
		elif self._value > self._max:
			self._value = self._max
			self._dir = -1

		self._on_change(self._value)

	def render(self, screen):
		super().render(screen)
		x, y = self.get_position()
		width, height = self.get_size()

		style = self.get_style()

		# Draw the slider track
		draw_rect_opacity(
			screen,
			style.slider_track_color,
			style.slider_track_opacity,
			(x + style.slider_handle_radius, y + height // 2 - style.slider_track_width // 2, width - style.slider_handle_radius * 2, style.slider_track_width),
			style.slider_track_width // 2
		)

		# Draw the slider handle
		handle_x = (self._value - self._min) / (self._max - self._min) * (width - style.slider_handle_radius * 2) + style.slider_handle_radius

		draw_circle_opacity(
			screen,
			style.slider_handle_color,
			style.slider_handle_opacity,
			(x + handle_x, y + height // 2),
			style.slider_handle_radius
		)

		# Draw the slider handle border
		draw_circle_opacity(
			screen,
			style.slider_handle_border_color,
			style.slider_handle_border_opacity,
			(x + handle_x, y + height // 2),
			style.slider_handle_radius,
			style.slider_handle_border_width
		)
	
	def get_size(self):
		width, height = super().get_size()

		style = self.get_style()

		width += self._width
		height += style.slider_handle_radius * 2

		return width, height
