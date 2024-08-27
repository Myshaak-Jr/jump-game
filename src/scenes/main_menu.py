import pygame
from core import IScene
from core.app_state import app_state as app_state
from gui import ImageElement, LabelElement, ButtonModifier, HCenterContainer, Container, Style, HSeparatorElement, OffsetModifier
import util.asset_manager as am
import util.language_manager as lm
import util.logger as log
from styles import COLOR_RED, COLOR_WHITE, BUTTON_STYLE, BUTTON_STYLE_HOVERED, BUTTON_STYLE_PRESSED, BUTTON_STYLE_PRESSED, LABEL_STYLE, HEADER_STYLE


class MainMenuScene(IScene):
	name = "main_menu"
	def __init__(self) -> None:
		try:
			with open("assets/savefile.txt", "r") as file:
				self.last_level = file.read()
		except FileNotFoundError:
			self.last_level = "luminis"

		# create the GUI
		self.gui = Container(width=app_state.width, height=app_state.height).with_children(
			ImageElement(am.get_image("assets/image/gui/background.png", app_state.width)),
			ImageElement(am.get_image("assets/image/gui/moon.png", app_state.width // 2), top = -25, left = -25),
			ButtonModifier(
				ImageElement(am.get_image("assets/image/gui/settings.png", app_state.width * 0.1)),
				on_click = lambda: log.info("Settings"),
				left = 20,
				bottom = 20,
				_style_hovered = Style(image_darken=0.2),
				_style_pressed = Style(image_darken=0.2, image_rotation=90)
			),
			LabelElement(
				"© Matěj Smetana",
				style=LABEL_STYLE,
				right = 20,
				bottom = 20
			),
			HCenterContainer(app_state.width / 2, 25, left = app_state.width / 2 - 40, top = 30).with_children(
				LabelElement(lm.get("general.title"), style=HEADER_STYLE),
				OffsetModifier(HSeparatorElement(app_state.width // 2, color=COLOR_WHITE), 0, -15),
				ButtonModifier(
					LabelElement(lm.get("gui.button.play")),
					on_click=lambda: app_state.queue_scene("level", self.last_level),
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