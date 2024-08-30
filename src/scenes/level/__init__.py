from __future__ import annotations
import math
from typing import override
from core import IScene, app_state, PlanetData
import pygame
from gui import Container, Style, ButtonModifier, ImageElement
from gui.containers.flex_container import Alignment, Direction, FlexContainer, Justification
from gui.elements.label_element import LabelElement
from gui.elements.slider_element import SliderElement
from scenes.level.util import GLOBAL_SCALE
from styles import SMALL_LABEL_STYLE
import util.language_manager as lm
import util.asset_manager as am
from util.my_math import IVec2, Vec2
from .camera import Camera
from .player import Player
from .tile import TileSprite, TileCollider
import pymunk


__all__ = [
	"LevelScene",
]


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


type HColliderGroup = list[IVec2]
type VColliderGroup = list[HColliderGroup]


class LevelScene(IScene):
	@override
	@classmethod
	def get_name(cls) -> str: return "level"

	def __init__(self, planet: PlanetData) -> None:
		self._planet = planet

		# Setup the space
		self._space = pymunk.Space()
		self._space.gravity = 0, self._planet.gravity

		# Setup the planet and level
		if planet.current_level >= len(planet.levels):
			raise ValueError("Invalid level ID")
		self._level = planet.levels[planet.current_level]
		
		# Tiles
		self._tile_colliders: list[TileCollider] = []
		self._tile_sprites: list[TileSprite] = []

		self._level_size = Vec2(0, 0)
		self._load_level()

		# Setup the player
		self._player_data = app_state.get_player_data()

		self._player = Player(self._space, 0.0, 0.0 , 0.5 * GLOBAL_SCALE, self._planet, self._player_data)
		self._player.set_pos(self._calc_start_pos())

		# Setup the camera and player
		self._camera = Camera(int(60 / GLOBAL_SCALE), 20.0)
		self._camera.follow_object(self._player, Vec2(0.2, 0.6))


		# Setup the GUI and Caption
		self._setup_gui()
		pygame.display.set_caption(lm.get("caption.driving_on").format(lm.get(self._planet.translation_key)))

	def get_planet(self) -> PlanetData:
		return self._planet
	
	def update_game_content(self, dt: float) -> None:
		self._player.update()

		self._space.step(dt)
		self._player.update_rect()

		for tile in self._tile_colliders:
			tile.update()
		self._camera.update(dt, self._level_size)

	def render_game_content(self, screen: pygame.Surface) -> None:
		for tile in self._tile_sprites:
			tile.render(screen, self._camera)

		if app_state.show_bounds():
			for tile in self._tile_colliders:
				tile.render(screen, self._camera)

		self._player.render(screen, self._camera)

	@override
	def handle_event(self, event: pygame.event.Event) -> None:
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				app_state.queue_scene("pause_menu", self)
	
	@override
	def update(self, dt: float) -> None:
		if app_state.show_fps():
			self._fps_counter.set_text(f"FPS: {math.floor(1 / dt)}")

		self.update_game_content(dt)

		if not self._player.is_alive(self._level_size):
			app_state.queue_scene("game_over", self)

		self._check_win()

		self._gui.update(dt)

	@override
	def render(self, screen: pygame.Surface) -> None:
		screen.fill((0, 0, 0))

		self.render_game_content(screen)

		self._gui.render(screen)

		pygame.display.flip()

	@override
	def on_enter(self) -> None:
		if not app_state.is_thrust_debug():
			pygame.mouse.set_visible(False)
		else:
			pygame.mouse.set_visible(True)

	@override
	def on_exit(self) -> None:
		pygame.mouse.set_visible(True)
		self._gui.on_scene_exit()

	def _calc_start_pos(self) -> Vec2:
		return Vec2(0.5 * GLOBAL_SCALE - self._player.get_width() / 2, self._calc_start_y() - self._player.get_height())

	def _calc_start_y(self) -> float:
		for y in range(self._level.height):
			if y == 0 or self._level.level_data[y-1][0] == "#":
				continue
			if self._level.level_data[y][0] == "#":
				return y * GLOBAL_SCALE
		raise ValueError("Invalid level data")

	def _add_tile_collider(self, x: int, y: int, width: int = 1, height: int = 1) -> None:
		# if y == 0:
		# 	height += 50
		# 	y -= 50
		
		tile = TileCollider(self._space, x * GLOBAL_SCALE, y * GLOBAL_SCALE, width * GLOBAL_SCALE, height * GLOBAL_SCALE)
		self._tile_colliders.append(tile)

	def _add_tile_sprite(self, x: int, y: int) -> None:
			self._tile_sprites.append(TileSprite(
				x * GLOBAL_SCALE,
				y * GLOBAL_SCALE,
				GLOBAL_SCALE,
				GLOBAL_SCALE,
				"assets/image/tiles/debug_tile.png",
			))

	def _load_level(self) -> None:
		self._level_size = Vec2(self._level.width * GLOBAL_SCALE, self._level.height * GLOBAL_SCALE)


		# Group the colliders
		h_collider_groups: dict[int, list[HColliderGroup]] = {}

		for y in range(self._level.height):
			nth = 0
			for x in range(self._level.width):
				if self._level.level_data[y][x] != "#": continue
				pos = IVec2(x, y)
				is_left = x == 0 or self._level.level_data[y][x-1] != "#"

				if is_left:
					nth = 0
					if x in h_collider_groups:
						h_collider_groups[x].append([pos])
					else:
						h_collider_groups[x] = [[pos]]
				else:
					nth += 1
					h_collider_groups[x - nth][-1].append(pos)

		# Group the colliders vertically
		v_collider_groups: list[VColliderGroup] = []

		for _, collumn in h_collider_groups.items():
			for i, group in enumerate(collumn):
				pos = group[0]
				width = len(group)
				
				if i == 0:
					v_collider_groups.append([group])
				
				else:
					# Check if the group is connected to the previous group
					prev_group = v_collider_groups[-1][-1]
					if len(prev_group) == width and prev_group[0].y == pos.y - 1:
						v_collider_groups[-1].append(group)
					else:
						v_collider_groups.append([group])

		# Create the colliders
		for group in v_collider_groups:
			pos = group[0][0]
			width = len(group[0])
			height = len(group)
			
			self._add_tile_collider(pos.x, pos.y, width, height)

		# Create the sprites
		for y in range(self._level.height):
			for x in range(self._level.width):
				if self._level.level_data[y][x] == "#":
					self._add_tile_sprite(x, y)
		
	def _check_win(self) -> None:
		if self._player.get_x() > self._level_size.x - 1:
			app_state.queue_scene("win_menu", self)

	def _setup_gui(self) -> None:		
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

		if app_state.show_fps():
			self._fps_counter = LabelElement("FPS: 0", style=SMALL_LABEL_STYLE.updated(Style(text_color=(255, 0, 0))), right=20, bottom=20)
			self._gui.add_child(self._fps_counter)

		if app_state.is_thrust_debug():
			self._thrust_label = LabelElement(SLIDER_THRUST_TEXT.format(self._player_data.thrust), style=SMALL_LABEL_STYLE)
			self._thrust_label_decay = LabelElement(SLIDER_THRUST_TEXT.format(self._player_data.thrust_decay), style=SMALL_LABEL_STYLE)
	
			self._gui.add_child(
				FlexContainer(
					app_state.get_width() / 2,
					direction=Direction.COLUMN,
					align=Alignment.END,
					gap=25,
					right=30,
					top=60,
				).with_children(
					FlexContainer(app_state.get_width() * 0.4, justify=Justification.SPACE_BETWEEN).with_children(
						self._thrust_label,
						SliderElement(
							width=150.0,
							min_value=10.0,
							max_value=100.0,
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

	def _update_player_thrust(self, value: float) -> None:
		self._player_data.thrust = value
		self._thrust_label.set_text(SLIDER_THRUST_TEXT.format(value))

	def _update_player_thrust_decay(self, value: float) -> None:
		self._player_data.thrust_decay = value
		self._thrust_label_decay.set_text(SLIDER_THRUST_DECAY_TEXT.format(value))
