from __future__ import annotations
from typing import override
from core import IScene, app_state, PlanetData
import pygame
from gui import Container, Style, ButtonModifier, ImageElement
from gui.containers.flex_container import Alignment, Direction, FlexContainer, Justification
from gui.elements.label_element import LabelElement
from gui.elements.slider_element import SliderElement
from styles import FOOTER_STYLE
import util.language_manager as lm
import util.asset_manager as am
from .camera import Camera
from .player import Player
from .tile import Tile
from .collision import sided_aabb, Side
from pygame.math import Vector2
import util.logger as log


SLIDER_STYLE = Style(
	slider_track_color=(200, 200, 200),
	slider_handle_color=(100, 100, 100),
	slider_handle_border_color=(255, 255, 255)
)

SLIDER_STYLE_HOVERED = Style(
	slider_handle_color=(120, 120, 120),
)

SLIDER_STYLE_PRESSED = Style(
	slider_handle_color=(160, 160, 160),
)


SLIDER_THRUST_TEXT = "Thrust: {:.3f}"
SLIDER_THRUST_DECAY_TEXT = "Thrust Decay: {:.3f}"


class LevelScene(IScene):
	def __init__(self, planet: PlanetData) -> None:
		self._planet = planet
		self._player_data = app_state.get_player_data()
		self._thrust_label = LabelElement(SLIDER_THRUST_TEXT.format(self._player_data.thrust), style=FOOTER_STYLE)
		self._thrust_label_decay = LabelElement(SLIDER_THRUST_TEXT.format(self._player_data.thrust_decay), style=FOOTER_STYLE)
		
		pygame.display.set_caption(lm.get("caption.driving_on").format(lm.get(self._planet.translation_key)))

		self._gui = Container(app_state.get_width(), app_state.get_height()).with_children(
			ButtonModifier(
				ImageElement(am.get_image("assets/image/gui/pause.png", app_state.get_width() * 0.1)),
				on_click = lambda: app_state.queue_scene("pause_menu", self),
				left = 20,
				top = 20,
				style_hovered = Style(image_darken=0.2),
				style_pressed = Style(image_darken=0.2, image_scale=1.1),
			)
		)

		if app_state.is_debug():
			self._gui.add_child(
				FlexContainer(
					app_state.get_width() / 2,
					direction=Direction.COLUMN,
					align=Alignment.END,
					gap=25,
					right=30,
					top=30,
				).with_children(
					FlexContainer(app_state.get_width() * 0.4, justify=Justification.SPACE_BETWEEN).with_children(
						self._thrust_label,
						SliderElement(
							width=150.0,
							min_value=100.0,
							max_value=800.0,
							default=self._player_data.thrust,
							on_changed=self._update_player_thrust,
							style=SLIDER_STYLE,
							style_hovered=SLIDER_STYLE_HOVERED,
							style_held=SLIDER_STYLE_PRESSED
						),
					),
					FlexContainer(app_state.get_width() * 0.4, justify=Justification.SPACE_BETWEEN).with_children(
						self._thrust_label_decay,
						SliderElement(
							width=150.0,
							min_value=0.0,
							max_value=1.0,
							default=self._player_data.thrust_decay,
							on_changed=self._update_player_thrust_decay,
							style=SLIDER_STYLE,
							style_hovered=SLIDER_STYLE_HOVERED,
							style_held=SLIDER_STYLE_PRESSED
						)
					)
				)
			)
		
		if planet.current_level >= len(planet.levels):
			raise ValueError("Invalid level ID")
		
		self._level = planet.levels[planet.current_level]
		self._load_level()

		self._camera = Camera(65)

		self._player = Player(app_state.get_player_data(), planet)
		self._player.set_position(self._calc_start_pos())
		self._player.set_velocity(self._planet.game_speed, 0)

	def get_planet(self) -> PlanetData:
		return self._planet

	def _update_player_thrust(self, value: float) -> None:
		self._player_data.thrust = value
		self._thrust_label.set_text(SLIDER_THRUST_TEXT.format(value))

	def _update_player_thrust_decay(self, value: float) -> None:
		self._player_data.thrust_decay = value
		self._thrust_label_decay.set_text(SLIDER_THRUST_DECAY_TEXT.format(value))

	def _calc_start_pos(self) -> Vector2:
		return Vector2(0.5 - self._player.get_width() / 2, self._calc_start_y() - self._player.get_height())

	def _calc_start_y(self) -> float:
		for y in range(self._level.height):
			if y == 0 or self._level.level_data[y-1][0] == "#":
				continue
			if self._level.level_data[y][0] == "#":
				return y
		raise ValueError("Invalid level data")

	def _add_tile(self, x: float, y: float) -> None:
		if y == 0:
			self.tiles.append(Tile(x, y - 31, 1, 32)) # you can't fly over that
		else:
			self.tiles.append(Tile(x, y))

	def _load_level(self) -> None:
		# TODO: possibly joid inner tiles into more bigger ones, this could optimize the collision detection and rendering
		self.tiles: list[Tile] = []
		for y in range(self._level.height):
			for x in range(self._level.width):
				if self._level.level_data[y][x] == "#":
					self._add_tile(x, y)

	@override
	def handle_event(self, event: pygame.event.Event) -> None:
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				app_state.queue_scene("pause_menu", self)
	
	def _kill(self) -> None:
		app_state.queue_scene("game_over", self)

	def _collide(self) -> None:
		if self._player.get_y() > self._level.height:
			self._kill()

		self._player.on_ground = False

		for tile in self.tiles:
			side = sided_aabb(self._player, tile)
			if side == Side.TOP:
				self._player.on_ground = True
				self._player.stop_y_movement(tile.get_y() - self._player.get_height())
			elif side == Side.BOTTOM:
				self._player.stop_y_movement(tile.get_y() + tile.get_width())
			elif side == Side.LEFT or side == Side.RIGHT:
				self._kill()

	def _check_win(self) -> None:
		if self._player.get_x() > self._level.width - 1:
			app_state.queue_scene("win_menu", self)

	@override
	def update(self, dt: float) -> None:
		self._player.update(dt)
		self._check_win()
		self._collide()
		self._gui.update(dt)
		self._camera.follow_object(self._player, self._level)

	def render_game_content(self, screen: pygame.Surface) -> None:
		for tile in self.tiles:
			tile.render(screen, self._camera)

		self._player.render(screen, self._camera)

	@override
	def render(self, screen: pygame.Surface) -> None:
		screen.fill((0, 0, 0))

		self.render_game_content(screen)
		self._gui.render(screen)

		pygame.display.flip()

	@override
	def on_enter(self) -> None:
		pass

	@override
	def on_exit(self) -> None:
		log.info("Exiting level scene")
		self._gui.on_scene_exit()

	@override
	@classmethod
	def get_name(cls) -> str:
		return "level"
