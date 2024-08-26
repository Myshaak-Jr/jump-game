import pygame
from numbers import Number


_images: dict[str, pygame.Surface] = {}
_fonts: dict[tuple[str, int], pygame.font.Font] = {}


def get_image(path: str, size: int | tuple[int, int] | None) -> pygame.Surface:
	if path not in _images:
		_images[path] = pygame.image.load(path).convert_alpha()
	image = _images[path]

	if isinstance(size, Number):
		size = (size, size * image.get_height() // image.get_width())
	if size is not None:
		image = pygame.transform.scale(image, size)
	return image

def get_font(path: str = None, size: int = 12) -> pygame.font.Font:
	if not pygame.font.get_init():
		pygame.font.init()

	if (path, size) not in _fonts:
		_fonts[(path, size)] = pygame.font.Font(path, size)
	return _fonts[(path, size)]