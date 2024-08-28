import pygame
from core import IScene, app_state, PlanetData
from gui import ImageElement, LabelElement, ButtonModifier, ColumnContainer, Container, Style, HSeparatorElement, OffsetModifier, Alignment, RowContainer, SliderElement
import util.asset_manager as am
import util.language_manager as lm
import util.logger as log
from styles import DEBUG_STYLE, COLOR_WHITE, BUTTON_STYLE, BUTTON_STYLE_HOVERED, BUTTON_STYLE_PRESSED, BUTTON_STYLE_PRESSED, LABEL_STYLE, HEADER_STYLE
import json


class AudioSettingsScene(IScene):
	def __init__(self) -> None:
		try:
			with open("data/save_file.json", "r") as file:
				json_data = json.load(file)
				self.last_planet = app_state.get_planet_data(int(json_data["last_planet_id"]))
				self.last_planet.current_level = int(json_data["last_level_id"])
		except FileNotFoundError:
			self.last_planet = app_state.get_planet_data(0)

		# create the GUI
		self.gui = Container(width=app_state.width, height=app_state.height).with_children(
			ImageElement(am.get_image("assets/image/gui/background.png", app_state.width)),
			ImageElement(am.get_image("assets/image/gui/moon.png", app_state.width // 2), top = -25, left = -25),
			ButtonModifier(
				ImageElement(am.get_image("assets/image/gui/arrow_back.png", app_state.width * 0.1)),
				on_click = lambda: app_state.queue_scene("main_menu"),
				left = 20,
				bottom = 20,
				style_hovered = Style(image_darken=0.2),
				style_pressed = Style(image_darken=0.2, image_scale=1.1)
			),
			LabelElement(
				"© Matěj Smetana",
				style=LABEL_STYLE,
				right = 20,
				bottom = 20
			),
			ColumnContainer(app_state.width / 2, align=Alignment.START, min_gap = 25, left = app_state.width / 2 - 40, top = 200).with_children(
				RowContainer(30, gap = 25).with_children(
					LabelElement(lm.get("gui.label.audio.master"), style=LABEL_STYLE),
					SliderElement(min=0, max=100, default=100, step=1, width=app_state.width / 4,
						on_change=lambda value: log.info(f"Master volume: {value}")
					)
				)
			)
		)

		pygame.display.set_caption(lm.get("general.title"))

	def _handle_event(self, event: pygame.event.Event) -> None | IScene:
		pass
 
	def update(self, dt: float) -> None | IScene:
		self.gui.update(dt)

	def render(self, screen: pygame.Surface) -> None:
		screen.fill((0, 0, 0))

		self.gui.render(screen)

		pygame.display.flip()
	
	@classmethod
	def get_name(cls) -> str:
		return "settings_video"
