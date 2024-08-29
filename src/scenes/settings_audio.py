from typing import override
import pygame
from core import IScene, app_state
from gui import ImageElement, LabelElement, ButtonModifier, Container, Style, Alignment, SliderElement
from gui.containers.flex_container import Direction, FlexContainer, Justification
import util.asset_manager as am
import util.language_manager as lm
import util.logger as log
from styles import LABEL_STYLE
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
		self._gui = Container(width=app_state.get_width(), height=app_state.get_height()).with_children(
			ImageElement(am.get_image("assets/image/gui/background.png", app_state.get_width())),
			ImageElement(am.get_image("assets/image/gui/moon.png", app_state.get_width() // 2), top = -25, left = -25),
			ButtonModifier(
				ImageElement(am.get_image("assets/image/gui/arrow_back.png", app_state.get_width() // 10)),
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
			FlexContainer(app_state.get_width() // 2, direction=Direction.COLUMN, align=Alignment.START, gap = 25, left = app_state.get_width() // 2 - 40, top = 200).with_children(
				FlexContainer(app_state.get_width() // 2, justify=Justification.SPACE_BETWEEN).with_children(
					LabelElement(lm.get("gui.label.audio.master"), style=LABEL_STYLE),
					SliderElement(min_value=0, max_value=100, default=100, step=1, width=app_state.get_width() / 4,
						on_changed=lambda value: log.info(f"Master volume: {value}")
					)
				)
			)
		)

		pygame.display.set_caption(lm.get("general.title"))

	def handle_event(self, event: pygame.event.Event) -> None:
		pass
 
	def update(self, dt: float) -> None:
		self._gui.update(dt)

	def render(self, screen: pygame.Surface) -> None:
		screen.fill((0, 0, 0))

		self._gui.render(screen)

		pygame.display.flip()
	
	@classmethod
	def get_name(cls) -> str:
		return "settings_video"

	@override
	def on_enter(self) -> None:
		pass

	@override
	def on_exit(self) -> None:
		self._gui.on_scene_exit()
