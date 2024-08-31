from collections.abc import Callable
import os
import pygame
from core.structs import PlanetData
from scenes.level.camera import Camera
import util.asset_manager as am
from util.my_math import Vec2, IVec2


class BackgroundLayer:
	def __init__(self, speed: float, sprite: str):
		self._speed = speed
		self._sprite = am.get_image(sprite)

		self._last_size: IVec2 | None = None
		self._cached_sprite: pygame.Surface | None = None

	def render(self, screen: pygame.Surface, camera: Camera, level_size: Vec2):
		level_screen_size = camera.apply_size(level_size)
		pos = camera.apply_pos(Vec2(0, 0))

		new_height = int(level_screen_size.y)
		new_width = int(new_height * self._sprite.get_width() / self._sprite.get_height())
		new_size = IVec2(new_width, new_height)

		if self._last_size != new_size or self._cached_sprite is None:
			self._cached_sprite = pygame.transform.scale(self._sprite, (new_width, new_height))
			self._last_size = IVec2(new_width, new_height)
		
		for x in range(0, level_screen_size.x, new_width):
			screen.blit(self._cached_sprite, (x + pos.x * self._speed, pos.y * self._speed))


class Background:
	def __init__(self, planet: PlanetData, speed_func: Callable[[float], float]):
		self._layers: list[BackgroundLayer] = []
		background_files = sorted([file for file in os.listdir(f"assets/image/background/{planet.name}/") if file.endswith(".png")])
		num_files = len(background_files)
		for i, file in enumerate(background_files):
			self._layers.append(BackgroundLayer(speed_func(i/num_files), f"assets/image/background/{planet.name}/{file}"))
	
	def render(self, screen: pygame.Surface, camera: Camera, level_size: Vec2):
		for layer in self._layers:
			layer.render(screen, camera, level_size)