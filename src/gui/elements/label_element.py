import pygame
from ..base import GUIElement
from ..style import AnyStyle


class LabelElement(GUIElement):
	def __init__(self, text: str, *, left: float | None = None, right: float | None = None, top: float | None = None, bottom: float | None = None, style: AnyStyle | None = None):
		super().__init__(
			left=left,
			right=right,
			top=top,
			bottom=bottom,
			style=style
		)
		self._text = text

	def get_text(self) -> str:
		return self._text
	
	def set_text(self, text: str) -> None:
		self._text = text

	def render(self, screen: pygame.Surface):
		super().render(screen)
		style = self.get_style()
		color = (style.text_color[0], style.text_color[1], style.text_color[2], int(255 * style.text_opacity))
		pos = self.get_position()
		pos = (pos[0] + style.padding_x, pos[1] + style.padding_y)
		text_surface = style.font.render(self._text, True, color)
		screen.blit(text_surface, pos)

	def get_size(self) -> tuple[float, float]:
		style = self.get_style()
		width, height = style.font.size(self._text)

		super_size = super().get_size()

		return width + super_size[0], height + super_size[1]
