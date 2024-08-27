from core import IScene, app_state, PlanetData, Level
import pygame
from gui import Container, LabelElement, Style, ButtonModifier, HCenterContainer, VCenterContainer, OffsetModifier, HSeparatorElement
from styles import LABEL_STYLE, HEADER_STYLE, BUTTON_STYLE, BUTTON_STYLE_HOVERED, BUTTON_STYLE_PRESSED, COLOR_WHITE
import util.language_manager as lm
from .level import LevelScene
import util.logger as log


class WinScene(IScene):
	def __init__(self, last_level: LevelScene) -> None:
		self.last_level = last_level

		# create the GUI
		self.gui = Container(width=app_state.width, height=app_state.height, style=Style()).with_children(
			HCenterContainer(app_state.width, 25, top = app_state.height / 4).with_children(
				LabelElement(lm.get("gui.label.win"), style=HEADER_STYLE),
				OffsetModifier(HSeparatorElement(app_state.width // 2, color=COLOR_WHITE), 0, -15),
				VCenterContainer(app_state.height / 20, 25).with_children(
					ButtonModifier(
						LabelElement(lm.get("gui.button.next_level")),
						on_click=lambda: log.info("Next level"),
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

	def handle_event(self, event: pygame.event.Event) -> None:
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				app_state.queue_scene(self.last_level)
	
	def update(self, dt: float) -> None:
		self.gui.update(dt)

	def render(self, screen: pygame.Surface) -> None:
		screen.fill((0, 0, 0))

		self.last_level.render_game_content(screen)
		screen.blit(self.darken, (0, 0))
		self.gui.render(screen)

		pygame.display.flip()

	@classmethod
	def get_name(cls) -> str:
		return "win"