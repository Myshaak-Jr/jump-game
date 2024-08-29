from collections.abc import Callable
import pygame
from ..base import GUIElement
from util.draw import draw_rect_opacity
from ..style import FullStyle, Style


__all__ = ['SliderElement']


DEFAULT_STYLE_HOVERED = Style(
	slider_handle_color=(127, 127, 127),
)

DEFAULT_STYLE_HELD = Style(
	slider_handle_color=(255, 255, 255),
)

class SliderElement(GUIElement):
	def __init__(self, *,
			  width: float,
			  min_value: float,
			  max_value: float,
			  default: float = 0,
			  step: float = 1,
			  on_changed: Callable[[float], None] | None = None,
			  left: float | None = None,
			  right: float | None = None,
			  top: float | None = None,
			  bottom: float | None = None,
			  style: Style = Style(), style_hovered: Style = DEFAULT_STYLE_HOVERED, style_held: Style = DEFAULT_STYLE_HELD):
		super().__init__(
			left=left,
			right=right,
			top=top,
			bottom=bottom,
			style=style
		)
		self._width = width
		self._min = min_value
		self._max = max_value
		self._value = min(max_value, max(min_value, default))
		self._step = step
		self._on_changed = on_changed
		self._held = False

		self._style_hovered = style_hovered
		self._style_held = style_held

		self._pressed = False
		self._hovered = False
	
		self._dir = 1

		if self._on_changed is not None:
			self._on_changed(self._value)

	def on_changed(self, func: Callable[[float], None]) -> None:
		self._on_changed = func

	def set_value(self, value: float):
		self._value = value

	def get_value(self):
		return self._value

	def _get_handle_x(self) -> float:
		style = self.get_style()
		width, _ = self.get_size()

		handle_x = (self._value - self._min) / (self._max - self._min) * (width - style.slider_handle_radius * 2) + style.slider_handle_radius

		return handle_x

	def update(self, dt: float):
		if GUIElement.pressed_element is not None and GUIElement.pressed_element != self: return

		mouse_x, mouse_y = pygame.mouse.get_pos()
		pressed = pygame.mouse.get_pressed()[0]

		style = self.get_style()
		x, y = self.get_position()

		x += style.padding_x
		y += style.padding_y
		
		handle_x = self._get_handle_x()

		self._hovered = (mouse_x - x - handle_x) ** 2 + (mouse_y - y - style.slider_handle_radius) ** 2 <= style.slider_handle_radius ** 2

		if not self._held and pressed and self._hovered:
			self._held = True
			GUIElement.pressed_element = self
		elif self._held and not pressed:
			self._held = False
			GUIElement.pressed_element = None
		elif self._held:
			dx = mouse_x - x - handle_x
			self._value += dx / (self._width - style.slider_handle_radius * 2) * (self._max - self._min)
			self._value = min(self._max, max(self._min, self._value))
			if self._on_changed is not None:
				self._on_changed(self._value)

	def render(self, screen: pygame.Surface):
		super().render(screen)
		x, y = self.get_position()
		width, height = self.get_size()
		style = self.get_style()

		x += style.padding_x
		y += style.padding_y
		width -= style.padding_x * 2
		height -= style.padding_y * 2

		slider_rect = pygame.Rect(
			x + style.slider_handle_radius,
			y + height / 2 - style.slider_track_width / 2,
			width - style.slider_handle_radius * 2,
			style.slider_track_width
		)

		# Draw the slider track
		draw_rect_opacity(
			screen,
			style.slider_track_color,
			style.slider_track_opacity,
			slider_rect
		)

		# Draw the slider handle
		handle_x = self._get_handle_x()

		pygame.draw.circle(
			screen,
			style.slider_handle_color,
			(x + handle_x, y + height // 2),
			style.slider_handle_radius
		)

		# Draw the slider handle border
		pygame.draw.circle(
			screen,
			style.slider_handle_border_color,
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
	
	def get_style(self) -> FullStyle:
		style = super().get_style()

		if self._held:
			style = style.updated(self._style_held)
		elif self._hovered:
			style = style.updated(self._style_hovered)

		return style
