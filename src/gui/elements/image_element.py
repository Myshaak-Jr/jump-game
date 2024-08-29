import pygame
from ..base import GUIElement
from ..style import AnyStyle

	
class ImageElement(GUIElement):
	def __init__(self, image: pygame.Surface, *, left: float | None = None, right: float | None = None, top: float | None = None, bottom: float | None = None, style: AnyStyle | None = None):
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
		
		brighness = int(darken * 255)

		image = self._image.copy()
		dark = pygame.Surface((image.get_width(), image.get_height()), flags=pygame.SRCALPHA)
		dark.fill((brighness, brighness, brighness, 0))
		image.blit(dark, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
		self._darkened_cache[darken] = image
		return image

	def get_position(self) -> tuple[float, float]:
		x, y = super().get_position()
		style = self.get_style()

		if style.image_scale > 1:
			pass

		w0, h0 = self._image.get_size()
		w1, h1 = super().get_size()
		x -= (w0 + w1) * (style.image_scale - 1) / 2
		y -= (h0 + h1) * (style.image_scale - 1) / 2

		return x, y
	
	def get_raw_size(self) -> tuple[float, float]:
		width, height = self._image.get_size()
		super_size = super().get_size()
		return width + super_size[0], height + super_size[1]

	def render(self, screen: pygame.Surface) -> None:
		super().render(screen)
		
		image = self._image
		style = self.get_style()

		if style.image_darken > 0.01:
			image = self._get_darkened_image()

		image = pygame.transform.rotate(image, style.image_rotation)

		image_w, image_h = image.get_size()
		image = pygame.transform.scale(image, (int(image_w * style.image_scale), int(image_h * style.image_scale)))

		screen.blit(image, self.get_position())
	
	def get_size(self) -> tuple[float, float]:
		width, height = self._image.get_size()
		width *= self.get_style().image_scale
		height *= self.get_style().image_scale
		super_size = super().get_size()

		return width + super_size[0], height + super_size[1]
