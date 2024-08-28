import pygame
from pygame.math import Vector2


def draw_rect_opacity(surface: pygame.Surface, color: tuple[int, int, int], opacity: float, rect: pygame.Rect, border_width: int = 0,  border_radius: int = -1) -> None:
	x, y, width, height = rect
	alpha_surface = pygame.Surface((width, height), pygame.SRCALPHA)
	color = color[:3] + (opacity * 255,)
	pygame.draw.rect(alpha_surface, color, alpha_surface.get_rect(), border_width, border_radius=border_radius)
	surface.blit(alpha_surface, (x, y))

def draw_circle_opacity(surface: pygame.Surface, color: tuple[int, int, int], opacity: float, center: Vector2, radius: int, width: int = 0) -> None:
	x, y = center
	alpha_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
	color = color[:3] + (opacity * 255,)
	pygame.draw.circle(alpha_surface, color, (radius, radius), radius, width)
	surface.blit(alpha_surface, (x - radius, y - radius))

