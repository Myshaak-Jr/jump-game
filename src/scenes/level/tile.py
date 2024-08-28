import pygame
from .camera import Camera
from .collision import IHasAABB


class Tile(IHasAABB):
	def __init__(self, x: float, y: float, width: float = 1, height: float = 1) -> None:
		self.x = x
		self.y = y
		self.width = width
		self.height = height

	def get_x(self) -> float:
		return self.x

	def get_y(self) -> float:
		return self.y
	
	def get_width(self) -> float:
		return self.width
	
	def get_height(self) -> float:
		return self.height

	def render(self, screen: pygame.Surface, camera: Camera) -> None:
		if camera.clip(self): return
		rect = camera.apply(self)
		pygame.draw.rect(screen, (255, 255, 255), rect)
