from scenes.level.util import IHasPos, IHasRect
from core import app_state
import math
import pygame
from util import my_math
from util.my_math import IVec2, Vec2


__all__ = [
	"Camera"
]


class Camera(IHasRect):
	def __init__(self, zoom: int, easing_rate: float) -> None:
		self._pos = Vec2(0, 0)
		self._zoom = zoom
		self._easing_rate = easing_rate
		self._following: IHasPos | None = None
		self._relative_pos = Vec2(0.5)

	def zoom(self, delta: int) -> None:
		self._zoom += delta
		if self._zoom < 1:
			self._zoom = 1

	def get_zoom(self) -> int:
		return self._zoom

	def follow_object(self, obj: IHasPos, relative_pos: Vec2 = Vec2(0.5)) -> None:
		self._following = obj
		self._relative_pos = relative_pos

		self._pos = self._calc_target_pos()
	
	def _calc_target_pos(self) -> Vec2:
		if self._following is None: return self._pos

		obj_pos = self._following.get_pos()

		view_width = app_state.get_width() / self._zoom
		view_height = app_state.get_height() / self._zoom
		target_x = obj_pos.x - view_width * self._relative_pos.x
		target_y = obj_pos.y - view_height * self._relative_pos.y

		return Vec2(target_x, target_y)

	def update(self, dt: float, level_size: Vec2) -> None:
		if self._following is None: return

		target_pos = self._calc_target_pos()
		self._pos = my_math.ease(self._pos, target_pos, self._easing_rate, dt)

		# Clamp the camera to the level bounds
		new_x = min(max(self._pos.x, 0), level_size.x - app_state.get_width() / self._zoom)
		new_y = min(max(self._pos.y, 0), level_size.y - app_state.get_height() / self._zoom)
		self._pos = Vec2(new_x, new_y)

	def set_relative_position(self, relative_pos: Vec2) -> None:
		self._relative_pos = relative_pos

	def get_relative_position(self) -> Vec2:
		return self._relative_pos

	def set_position(self, x: float, y: float) -> None:
		self._pos = Vec2(x, y)

	def apply(self, obj: IHasRect) -> pygame.Rect:
		obj_rect = obj.get_rect()
		return self.apply_rect(obj_rect)
	
	def apply_rect(self, rect: pygame.FRect) -> pygame.Rect:
		new_x = math.floor((rect.x - self._pos.x) * self._zoom)
		new_y = math.floor((rect.y - self._pos.y) * self._zoom)
		new_w = math.ceil(rect.width * self._zoom)
		new_h = math.ceil(rect.height * self._zoom)

		return pygame.Rect(new_x, new_y, new_w, new_h)


	def apply_pos(self, point: Vec2) -> IVec2:
		new_x = math.floor((point.x - self._pos.x) * self._zoom)
		new_y = math.floor((point.y - self._pos.y) * self._zoom)

		return IVec2(new_x, new_y)

	def apply_size(self, size: Vec2) -> IVec2:
		new_w = math.ceil(size.x * self._zoom)
		new_h = math.ceil(size.y * self._zoom)
		return IVec2(new_w, new_h)
	
	def apply_inverse(self, rect: pygame.Rect) -> pygame.FRect:
		new_x = rect.x / self._zoom + self._pos.x
		new_y = rect.y / self._zoom + self._pos.y
		new_w = rect.width / self._zoom
		new_h = rect.height / self._zoom

		return pygame.FRect(new_x, new_y, new_w, new_h)
	
	def apply_inverse_pos(self, point: IVec2) -> Vec2:
		new_x = point.x / self._zoom + self._pos.x
		new_y = point.y / self._zoom + self._pos.y

		return Vec2(new_x, new_y)

	def apply_inverse_size(self, size: IVec2) -> Vec2:
		new_w = size.x / self._zoom
		new_h = size.y / self._zoom
		return Vec2(new_w, new_h)

	def clip(self, entity: IHasRect) -> bool:
		rect = entity.get_rect()
		view_rect = self.get_rect()

		if rect.x + rect.width < view_rect.x:
			return True
		if rect.x > view_rect.x + view_rect.width:
			return True
		if rect.y + rect.height < view_rect.y:
			return True
		if rect.y > view_rect.y + view_rect.height:
			return True

		return False
		
	
	def get_rect(self) -> pygame.FRect:
		return pygame.FRect(self._pos.x, self._pos.y, app_state.get_width() / self._zoom, app_state.get_height() / self._zoom)
	