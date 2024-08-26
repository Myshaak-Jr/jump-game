import pygame
from .base import IElement
from .style import Style


class LabelElement(IElement):
	def __init__(self, text: str, /, pos: tuple[int, int] = (0, 0), style: Style = Style()):
		super().__init__(pos, style)
		self._text = text

	def render(self, screen: pygame.Surface):
		super().render(screen)
		style = self.get_style()
		color = (style.text_color[0], style.text_color[1], style.text_color[2], 255 * style.text_opacity)
		pos = self.get_position()
		pos = (pos[0] + style.padding_x, pos[1] + style.padding_y)
		text_surface = style.font.render(self._text, True, color)
		screen.blit(text_surface, pos)

	def get_size(self) -> tuple[int, int]:
		style = self.get_style()
		width, height = style.font.size(self._text)
		width += style.padding_x * 2
		height += style.padding_y * 2
		return width, height
