import pygame
from .base import IElement
from .style import Style

	
class ImageElement(IElement):
	def __init__(self, image: pygame.Surface, /, pos: tuple[int, int] = (0, 0), style: Style = Style()):
		super().__init__(pos, style)
		self._image = image
	
	def render(self, screen: pygame.Surface) -> None:
		super().render(screen)
		screen.blit(self._image, self._pos)
	
	def get_size(self) -> tuple[int, int]:
		width, height = self._image.get_size()
		style = self.get_style()
		width += style.padding_x * 2
		height += style.padding_y * 2
		return width, height