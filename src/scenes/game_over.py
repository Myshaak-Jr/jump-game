from typing import override
import pygame
from core import IScene
from core import app_state
from gui import LabelElement, ButtonModifier, Container, Style, HSeparatorElement, OffsetModifier
from gui.containers.flex_container import Direction, FlexContainer
from util import my_math
import util.language_manager as lm
from styles import COLOR_WHITE, BUTTON_STYLE, BUTTON_STYLE_HOVERED, BUTTON_STYLE_PRESSED, HEADER_STYLE
from .level import LevelScene
from gui.elements.image_element import ImageElement
import util.asset_manager as am


class GameOverScene(IScene):
	def __init__(self, last_level: LevelScene) -> None:
		self._last_level = last_level
		self._slowmo_factor = 1

		# create the GUI
		self._background = ImageElement(
			am.get_image("assets/image/gui/background.png", app_state.get_width()),
			style=Style(image_opacity=0.0)
		)
		self._gui = Container(width=app_state.get_width(), height=app_state.get_height(), style=Style()).with_children(
			FlexContainer(app_state.get_width(), direction=Direction.COLUMN, gap = 25, top = app_state.get_height() / 4).with_children(
				LabelElement(lm.get("gui.label.game_over"), style=HEADER_STYLE),
				OffsetModifier(HSeparatorElement(app_state.get_width() // 2, color=COLOR_WHITE), 0, -15),
				FlexContainer(app_state.get_height() / 20, gap = 25).with_children(
					ButtonModifier(
						LabelElement(lm.get("gui.button.retry")),
						on_click=lambda: app_state.queue_scene("level", self._last_level.get_planet()),
						style=BUTTON_STYLE,
						style_hovered=BUTTON_STYLE_HOVERED,
						style_pressed=BUTTON_STYLE_PRESSED
					),
					ButtonModifier(
						LabelElement(lm.get("gui.button.main_menu")),
						on_click=lambda: app_state.queue_scene("main_menu"),
						style=BUTTON_STYLE,
						style_hovered=BUTTON_STYLE_HOVERED,
						style_pressed=BUTTON_STYLE_PRESSED
					)
				)
			)
		)

		pygame.display.set_caption(lm.get("general.title"))

		self._darkening_surface = pygame.Surface((app_state.get_width(), app_state.get_height()))
		self._darkening_surface.fill((0, 0, 0))

	def handle_event(self, event: pygame.event.Event) -> None:
		pass
 
	def update(self, dt: float) -> None:
		self._slowmo_factor = my_math.ease(self._slowmo_factor, 0.0, 0.3, dt)
		self._darkening_surface.set_alpha(int(255 * (1 - self._slowmo_factor)))

		self._background.update(dt)
		self._background.update_style(Style(image_opacity=(1.0 - self._slowmo_factor)))

		self._last_level.update_game_content(dt * self._slowmo_factor * 0.2)
		self._gui.update(dt)

	def render(self, screen: pygame.Surface) -> None:
		screen.fill((0, 0, 0))

		self._last_level.render_game_content(screen)

		screen.blit(self._darkening_surface, (0, 0))
		self._background.render(screen)
		self._gui.render(screen)

		pygame.display.flip()
	
	@classmethod
	def get_name(cls) -> str:
		return "game_over"

	@override
	def on_enter(self) -> None:
		pass

	@override
	def on_exit(self) -> None:
		self._gui.on_scene_exit()
