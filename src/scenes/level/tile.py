from typing import override
import pygame
import pymunk
from .camera import Camera
from .util import CollisionType, IHasRect
import util.asset_manager as am


__all__ = [
	"TileSprite",
	"TileCollider",
]


class TileSprite(IHasRect):
	def __init__(self, x: float, y: float, width: float, height: float, sprite: str, src_rect: pygame.Rect | None = None):
		self._color = (255, 255, 255)
		
		# Pygame representation
		self._rect = pygame.FRect(x, y, width, height)

		self._sprite = am.get_image(sprite)
		self._src_rect = src_rect

		# Cache for zoomed sprites
		self._last_zoom = 0
		self._zoom_cache: pygame.Surface | None = None
	
	@override
	def get_rect(self) -> pygame.FRect:
		return self._rect

	def render(self, screen: pygame.Surface, camera: Camera):
		if camera.clip(self): return
		rect = camera.apply(self)

		zoom = camera.get_zoom()

		if zoom != self._last_zoom or self._zoom_cache is None:
			new_width = int(self._rect.width * zoom)
			new_height = int(self._rect.height * zoom)
			if self._src_rect is not None:
				new_width *= self._src_rect.width / 64
				new_height *= self._src_rect.height / 64
				new_width = int(new_width) + 1
				new_height = int(new_height) + 1
				self._zoom_cache = pygame.transform.scale(self._sprite.subsurface(self._src_rect), (new_width, new_height))
			else:
				self._zoom_cache = pygame.transform.scale(self._sprite, (new_width, new_height))
			self._last_zoom = zoom
 
		screen.blit(self._zoom_cache, rect)


class TileCollider(IHasRect):
	def __init__(self, space: pymunk.Space, x: float, y: float, width: float, height: float):
		self._color = (255, 255, 255)
		
		# Pygame representation
		self._rect = pygame.FRect(x, y, width, height)
		
		# Pymunk representation
		self._body = pymunk.Body(body_type=pymunk.Body.STATIC)
		
		self._body.position = (x + width / 2, y + height / 2)
		self._shape = pymunk.Poly.create_box(self._body, (width, height))
		self._shape.density = 1
		self._shape.elasticity = 0.5
		self._shape.friction = 0.5  # You can adjust friction or other properties here
		self._shape.collision_type = CollisionType.GROUND.value
		
		# Add the shape to the space
		space.add(self._body, self._shape)
	
	def render(self, screen: pygame.Surface, camera: Camera):
		if camera.clip(self): return
		rect = camera.apply(self)
		pygame.draw.rect(screen, (255, 0, 0), rect, 3)
	
	@override
	def get_rect(self) -> pygame.FRect:
		return self._rect

	def update(self):
		# Update the position based on Pymunk simulation
		self._rect.x = self._body.position.x - self._rect.width / 2
		self._rect.y = self._body.position.y - self._rect.height / 2