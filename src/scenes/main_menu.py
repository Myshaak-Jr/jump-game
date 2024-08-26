import pygame
from core import IScene
from core.app_state import app_state as app_state
from gui import ImageElement, LabelElement, ButtonModifier, HCenterContainer, Container, Style
from .level_scene import LevelScene
import util.asset_manager as am
import util.language_manager as lm
import util.logger as log
from styles import COLOR_RED, BUTTON_STYLE, BUTTON_STYLE_HOVERED, BUTTON_STYLE_PRESSED, BUTTON_STYLE_PRESSED, LABEL_STYLE, HEADER_STYLE


class MainMenuScene(IScene):
	def __init__(self) -> None:
		# create the GUI
		self.gui = Container(pos=(0, 0), style=Style(border_color=COLOR_RED)).with_children(
			ImageElement(am.get_image("assets/image/gui/background.png", app_state.width)),
			ImageElement(am.get_image("assets/image/gui/moon.png", app_state.width // 2), pos=(0, 0)),
			ButtonModifier(
				ImageElement(am.get_image("assets/image/gui/settings.png", app_state.width * 0.1)),
				on_click=lambda: log.info("Settings"),
				pos=(20, app_state.height - app_state.width * 0.1 - 20),
			),
			LabelElement(
				"© Matěj Smetana",
				style=LABEL_STYLE,
				pos=(app_state.width / 2, app_state.height - 20),
			),
			HCenterContainer(app_state.width / 2, 20, pos=(app_state.width / 2, 30)).with_children(
				LabelElement(lm.get("general.title"), style=HEADER_STYLE),
				ButtonModifier(
					LabelElement(lm.get("gui.button.play")),
					on_click=lambda: app_state.queue_scene(LevelScene(1.0)),
					style=BUTTON_STYLE,
					_style_hovered=BUTTON_STYLE_HOVERED,
					_style_pressed=BUTTON_STYLE_PRESSED
				),
				ButtonModifier(
					LabelElement(lm.get("gui.button.level_select")),
					on_click=lambda: log.info(lm.get("caption.level_select")),
					style=BUTTON_STYLE,
					_style_hovered=BUTTON_STYLE_HOVERED,
					_style_pressed=BUTTON_STYLE_PRESSED
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