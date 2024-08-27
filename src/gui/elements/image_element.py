import pygame
from ..base import IElement
from ..style import Style
from typing import Optional

	
class ImageElement(IElement):
	def __init__(self, image: pygame.Surface, *, left: Optional[int] = None, right: Optional[int] = None, top: Optional[int] = None, bottom: Optional[int] = None, style: Style = Style()):
		super().__init__(
			left=left,
			right=right,
			top=top,
			bottom=bottom,
			style=style
		)
		self._image = image
		self._darkened_cache: dict[float, pygame.Surface] = {}

	
	def _get_darkened_image(self) -> pygame.Surface:
		darken = self.get_style().image_darken
		if darken in self._darkened_cache:
			return self._darkened_cache[darken]
		
		brighness = darken * 255

		image = self._image.copy()
		dark = pygame.Surface((image.get_width(), image.get_height()), flags=pygame.SRCALPHA)
		dark.fill((brighness, brighness, brighness, 0))
		image.blit(dark, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
		self._darkened_cache[darken] = image
		return image

	def render(self, screen: pygame.Surface) -> None:
		super().render(screen)
		
		image = self._image
		style = self.get_style()

		if style.image_darken > 0.01:
			image = self._get_darkened_image()

		screen.blit(pygame.transform.rotate(image, style.image_rotation), self.get_position())
	
	def get_size(self) -> tuple[int, int]:
		width, height = self._image.get_size()
		super_size = super().get_size()

		return width + super_size[0], height + super_size[1]
