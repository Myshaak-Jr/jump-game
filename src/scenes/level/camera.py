from .collision import IHasAABB, AABB, aabb
from core import app_state, LevelData
import math
import pygame
import util.logger as log


class Camera(IHasAABB):
	def __init__(self, zoom: float = 1.0) -> None:
		self._x = 0
		self._y = 0
		self._zoom = zoom

	@property
	def x(self) -> float:
		return self._x
	
	@property
	def y(self) -> float:
		return self._y
	
	def zoom(self, delta: float) -> None:
		self._zoom += delta
		if self._zoom < 0.1:
			self._zoom = 0.1
		log.info(f"Zoom: {self._zoom}")

	def follow_object(self, obj: IHasAABB, level: LevelData) -> None:
		RELATIVE_X = 0.2
		RELATIVE_Y = 0.2

		obj_rect = obj.get_rect()

		view_width = app_state.get_width() / self._zoom
		view_height = app_state.get_height() / self._zoom
		self._x = obj_rect.x - view_width * RELATIVE_X + obj_rect.width / 2
		self._y = obj_rect.y - view_height * RELATIVE_Y + obj_rect.height / 2

		# Clamp the camera to the level bounds
		if self._x < 0:
			self._x = 0
		if self._y < 0:
			self._y = 0
		if self._x + view_width > level.width:
			self._x = level.width - view_width
		if self._y + view_height > level.height:
			self._y = level.height - view_height
	
	def apply(self, obj: IHasAABB) -> pygame.Rect:
		obj_rect = obj.get_rect()

		new_x = math.floor((obj_rect.x - self._x) * self._zoom)
		new_y = math.floor((obj_rect.y - self._y) * self._zoom)
		new_w = math.ceil(obj_rect.width * self._zoom)
		new_h = math.ceil(obj_rect.height * self._zoom)

		return pygame.Rect(new_x, new_y, new_w, new_h)
	
	def get_x(self) -> float:
		return self._x
	
	def get_y(self) -> float:
		return self._y
	
	def get_width(self) -> float:
		return app_state.get_width() / self._zoom
	
	def get_height(self) -> float:
		return app_state.get_height() / self._zoom

	def clip(self, entity: IHasAABB) -> bool:
		return not aabb(self, entity)
