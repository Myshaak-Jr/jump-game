from __future__ import annotations
from core import IScene, app_state, PlanetData
import pygame
from gui import Container, Style, ButtonModifier, ImageElement
import util.language_manager as lm
import util.asset_manager as am
from .camera import Camera
from .player import Player
from .tile import Tile
from .collision import sided_aabb, Side
from pygame.math import Vector2


class LevelScene(IScene):
	def __init__(self, planet: PlanetData) -> None:
		self.planet = planet
		
		pygame.display.set_caption(lm.get("caption.driving_on").format(lm.get(self.planet.translation_key)))

		self._gui = Container().with_children(
			ButtonModifier(
				ImageElement(am.get_image("assets/image/gui/pause.png", app_state.width * 0.1)),
				on_click = lambda: app_state.queue_scene("pause_menu", self),
				left = 20,
				top = 20,
				style_hovered = Style(image_darken=0.2),
				style_pressed = Style(image_darken=0.2, image_scale=1.1),
			)
		)
		
		if planet.current_level >= len(planet.levels):
			raise ValueError("Invalid level ID")
		
		self.level = planet.levels[planet.current_level]
		self._load_level()

		self.camera = Camera(65)

		self.player = Player(app_state.get_player_data(), planet)
		self.player.set_position(self._calc_start_pos())
		self.player.set_velocity(self.planet.game_speed, 0)

	def _calc_start_pos(self) -> Vector2:
		return Vector2(0.5 - self.player.get_width() / 2, self._calc_start_y() - self.player.get_height())

	def _calc_start_y(self) -> float:
		for y in range(self.level.height):
			if y == 0 or self.level.level_data[y-1][0] == "#":
				continue
			if self.level.level_data[y][0] == "#":
				return y

	def _add_tile(self, x, y) -> None:
		if y == 0:
			self.tiles.append(Tile(x, y - 31, 1, 32)) # you can't fly over that
		else:
			self.tiles.append(Tile(x, y))

	def _load_level(self) -> None:
		# TODO: possibly joid inner tiles into more bigger ones, this could optimize the collision detection and rendering
		self.tiles: list[Tile] = []
		for y in range(self.level.height):
			for x in range(self.level.width):
				if self.level.level_data[y][x] == "#":
					self._add_tile(x, y)

	def handle_event(self, event: pygame.event.Event) -> None:
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				app_state.queue_scene("pause_menu", self)
	
	def _kill(self) -> None:
		app_state.queue_scene("game_over", self)

	def _collide(self) -> None:
		if self.player.get_y() > self.level.height:
			self._kill()

		self.player.on_ground = False

		for tile in self.tiles:
			side = sided_aabb(self.player, tile)
			if side == Side.TOP:
				self.player.on_ground = True
				self.player.stop_y_movement(tile.get_y() - self.player.get_height())
			elif side == Side.BOTTOM:
				self.player.stop_y_movement(tile.get_y() + tile.get_width())
			elif side == Side.LEFT or side == Side.RIGHT:
				self._kill()

	def _check_win(self) -> None:
		if self.player.get_x() > self.level.width - 1:
			app_state.queue_scene("win_menu", self)

	def update(self, dt: float) -> None:
		self.player.update(dt)
		self._check_win()
		self._collide()
		self._gui.update(dt)
		self.camera.follow_object(self.player, self.level)

	def render_game_content(self, screen: pygame.Surface) -> None:
		for tile in self.tiles:
			tile.render(screen, self.camera)

		self.player.render(screen, self.camera)

	def render(self, screen: pygame.Surface) -> None:
		screen.fill((0, 0, 0))

		self.render_game_content(screen)
		self._gui.render(screen)

		pygame.display.flip()
	
	@classmethod
	def get_name(cls) -> str:
		return "level"
