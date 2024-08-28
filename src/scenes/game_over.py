import pygame
from core import IScene
from core.app_state import app_state, PlanetData
from gui import ImageElement, LabelElement, ButtonModifier, ColumnContainer, RowContainer, Container, Style, HSeparatorElement, OffsetModifier, Alignment
import util.asset_manager as am
import util.language_manager as lm
import util.logger as log
from styles import COLOR_WHITE, BUTTON_STYLE, BUTTON_STYLE_HOVERED, BUTTON_STYLE_PRESSED, BUTTON_STYLE_PRESSED, LABEL_STYLE, HEADER_STYLE
from .level import LevelScene


class GameOverScene(IScene):
	def __init__(self, last_level: LevelScene) -> None:
		self.last_level = last_level

		# create the GUI
		self.gui = Container(width=app_state.width, height=app_state.height, style=Style()).with_children(
			ColumnContainer(app_state.width, min_gap = 25, top = app_state.height / 4).with_children(
				LabelElement(lm.get("gui.label.game_over"), style=HEADER_STYLE),
				OffsetModifier(HSeparatorElement(app_state.width // 2, color=COLOR_WHITE), 0, -15),
				RowContainer(app_state.height / 20, gap = 25).with_children(
					ButtonModifier(
						LabelElement(lm.get("gui.button.retry")),
						on_click=lambda: app_state.queue_scene("level", self.last_level.planet),
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

		self.darken = pygame.Surface((app_state.width, app_state.height))
		self.darken.fill((0, 0, 0))
		self.darken.set_alpha(128)

	def _handle_event(self, event: pygame.event.Event) -> None | IScene:
		pass
 
	def update(self, dt: float) -> None | IScene:
		self.gui.update(dt)

	def render(self, screen: pygame.Surface) -> None:
		screen.fill((0, 0, 0))

		self.last_level.render_game_content(screen)

		screen.blit(self.darken, (0, 0))

		self.gui.render(screen)

		pygame.display.flip()
	
	@classmethod
	def get_name(cls) -> str:
		return "game_over"