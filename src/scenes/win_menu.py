from typing import override
from core import IScene, app_state
import pygame
from gui import Container, LabelElement, Style, ButtonModifier, OffsetModifier, HSeparatorElement
from gui.containers.flex_container import Direction, FlexContainer
from styles import HEADER_STYLE, BUTTON_STYLE, BUTTON_STYLE_HOVERED, BUTTON_STYLE_PRESSED, COLOR_WHITE
import util.language_manager as lm
from .level import LevelScene


class WinMenuScene(IScene):
	def __init__(self, last_level: LevelScene) -> None:
		self.last_level = last_level

		next_level = app_state.get_next_level(self.last_level.get_planet())
		if next_level is None:
			next_scene_on_click = lambda: app_state.queue_scene("main_menu")#"credits"
			label_text = "gui.button.credits"
		else:
			next_scene_on_click = lambda: app_state.queue_scene("level", next_level)
			label_text = "gui.button.next_level"

		# create the GUI
		self._gui = Container(width=app_state.get_width(), height=app_state.get_height(), style=Style()).with_children(
			FlexContainer(app_state.get_width(), direction=Direction.COLUMN, gap = 25, top = app_state.get_height() / 4).with_children(
				LabelElement(lm.get("gui.label.win"), style=HEADER_STYLE),
				OffsetModifier(HSeparatorElement(app_state.get_width() // 2, color=COLOR_WHITE), 0, -15),
				FlexContainer(app_state.get_height() / 20, gap = 25).with_children(
					ButtonModifier(
						LabelElement(lm.get(label_text)),
						on_click=next_scene_on_click,
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
				),
				ButtonModifier(
					LabelElement(lm.get("gui.button.restart")),
					on_click=lambda: app_state.queue_scene("level", self.last_level.get_planet()),
					style=BUTTON_STYLE,
					style_hovered=BUTTON_STYLE_HOVERED,
					style_pressed=BUTTON_STYLE_PRESSED
				)
			)
		)

		pygame.display.set_caption(lm.get("general.title"))

		self.darken = pygame.Surface((app_state.get_width(), app_state.get_height()))
		self.darken.fill((0, 0, 0))
		self.darken.set_alpha(128)

	def handle_event(self, event: pygame.event.Event) -> None:
		pass
	
	def update(self, dt: float) -> None:
		self._gui.update(dt)

	def render(self, screen: pygame.Surface) -> None:
		screen.fill((0, 0, 0))

		self.last_level.render_game_content(screen)
		screen.blit(self.darken, (0, 0))
		self._gui.render(screen)

		pygame.display.flip()

	@classmethod
	def get_name(cls) -> str:
		return "win_menu"

	@override
	def on_enter(self) -> None:
		pass

	@override
	def on_exit(self) -> None:
		self._gui.on_scene_exit()