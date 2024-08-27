import pygame
from core import IScene
from core.app_state import app_state as app_state
from gui import ImageElement, LabelElement, ButtonModifier, HCenterContainer, VCenterContainer, Container, Style, HSeparatorElement, OffsetModifier
from .level_scene import LevelScene
import util.asset_manager as am
import util.language_manager as lm
import util.logger as log
from styles import COLOR_WHITE, BUTTON_STYLE, BUTTON_STYLE_HOVERED, BUTTON_STYLE_PRESSED, BUTTON_STYLE_PRESSED, LABEL_STYLE, HEADER_STYLE


class GameOverScene(IScene):
	name = "game_over"
	def __init__(self, planet: str) -> None:
		self.planet = planet

		# create the GUI
		self.gui = Container(width=app_state.width, height=app_state.height, style=Style()).with_children(
			ImageElement(am.get_image("assets/image/gui/background.png", app_state.width)),
			ImageElement(am.get_image(app_state.get_planet_data(planet)["sprite"], app_state.width // 2),
				top = -app_state.width // 3, left = -app_state.width // 3, style=Style(image_rotation=45)),
			HCenterContainer(app_state.width, 25, top = app_state.height / 4).with_children(
				LabelElement(lm.get("gui.label.game_over"), style=HEADER_STYLE),
				OffsetModifier(HSeparatorElement(app_state.width // 2, color=COLOR_WHITE), 0, -15),
				VCenterContainer(app_state.height / 20, 25).with_children(
					ButtonModifier(
						LabelElement(lm.get("gui.button.retry")),
						on_click=lambda: app_state.queue_scene("level", planet),
						style=BUTTON_STYLE,
						_style_hovered=BUTTON_STYLE_HOVERED,
						_style_pressed=BUTTON_STYLE_PRESSED
					),
					ButtonModifier(
						LabelElement(lm.get("gui.button.main_menu")),
						on_click=lambda: app_state.queue_scene("main_menu"),
						style=BUTTON_STYLE,
						_style_hovered=BUTTON_STYLE_HOVERED,
						_style_pressed=BUTTON_STYLE_PRESSED
					)
				)
			)
		)

		pygame.display.set_caption(lm.get("general.title"))

	def handle_event(self, event: pygame.event.Event) -> None | IScene:
		pass
 
	def update(self, dt: float) -> None | IScene:
		self.gui.update(dt)

	def render(self, screen: pygame.Surface) -> None:
		screen.fill((0, 0, 0))

		self.gui.render(screen)

		pygame.display.flip()