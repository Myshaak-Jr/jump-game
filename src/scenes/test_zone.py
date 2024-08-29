from typing import override
from core import IScene, app_state
import pygame
from gui import Container, FlexContainer, Style, ButtonModifier, LabelElement, Alignment, Justification, Direction
from random import random
from gui.elements.slider_element import SliderElement
import util.asset_manager as am
import util.logger as log


NUM_DUMMIES = 10

flex_width: float
flex_height: float

min_dummy_width: float
min_dummy_height: float

max_dummy_width: float
max_dummy_height: float

MAX_GAP = 40

DUMMY_STYLE = Style(
	border_color=(255, 0, 0),
	border_width=2,
	border_opacity=1,
)

def _create_dummy():
	return Container(
		width=random() * (max_dummy_width - min_dummy_width) + min_dummy_width,
		height=random() * (max_dummy_height - min_dummy_height) + min_dummy_height,
		style=DUMMY_STYLE
	)

BUTTON_STYLE = Style(
	text_color=(0, 0, 0),
	font=am.get_font("assets/font/Comfortaa-Regular.ttf", 20),
	background_color=(200, 200, 200),
	background_opacity=1,
	border_color=(35, 35, 35),
	border_opacity=1,
	border_width=2,
	padding_x=5,
	padding_y=5,
)

BUTTON_STYLE_HOVERED = Style(
	background_color=(170, 170, 170),
)

BUTTON_STYLE_PRESSED = Style(
	background_color=(120, 120, 120),
)


DIRECTIONS = list(Direction)
ALIGNMENTS = list(Alignment)
JUSTIFICATIONS = list(Justification)


class TestZoneScene(IScene):
	def __init__(self) -> None:
		global flex_width, flex_height, min_dummy_width, max_dummy_width, max_dummy_width, max_dummy_height
		flex_width = app_state.get_width() * 9 / 10
		flex_height = app_state.get_height() * 9 / 10

		max_dummy_width = flex_width / 9
		max_dummy_height = flex_height / 9

		min_dummy_width = max_dummy_width / 2
		max_dummy_width = max_dummy_height / 2

		self.current_direction = 0
		self.current_alignment = 0
		self.current_justification = 0

		self._target = FlexContainer(
			flex_width, flex_height,
			direction=DIRECTIONS[self.current_direction],
			align=ALIGNMENTS[self.current_alignment],
			justify=JUSTIFICATIONS[self.current_justification],
			style=DUMMY_STYLE
		).with_children(
			_create_dummy()
			for _ in range(NUM_DUMMIES)
		)

		self._target_wrapper = FlexContainer(app_state.get_width(), app_state.get_height(), justify=Justification.CENTER, align=Alignment.CENTER).with_children(
			self._target
		)

		self._tools = FlexContainer(direction=Direction.COLUMN, align=Alignment.END, gap=10, right=10, top=10).with_children(
			ButtonModifier(
				LabelElement("Change direction"),
				on_click=self._update_direction,
				style=BUTTON_STYLE,
				style_hovered=BUTTON_STYLE_HOVERED,
				style_pressed=BUTTON_STYLE_PRESSED
			),
			ButtonModifier(
				LabelElement("Change alignment"),
				on_click=self._update_alignment,
				style=BUTTON_STYLE,
				style_hovered=BUTTON_STYLE_HOVERED,
				style_pressed=BUTTON_STYLE_PRESSED
			),
			ButtonModifier(
				LabelElement("Change justification"),
				on_click=self._update_justification,
				style=BUTTON_STYLE,
				style_hovered=BUTTON_STYLE_HOVERED,
				style_pressed=BUTTON_STYLE_PRESSED
			),
			SliderElement(
				width=200,
				min_value=0,
				max_value=MAX_GAP,
				default=10,
				on_changed=self._update_gap,
			)
		)
	
	def _update_alignment(self) -> None:
		self.current_alignment = (self.current_alignment + 1) % len(ALIGNMENTS)
		log.info(f"Changing alignment to {ALIGNMENTS[self.current_alignment]}")
		self._target.set_alignment(ALIGNMENTS[self.current_alignment])
	
	def _update_justification(self) -> None:
		self.current_justification = (self.current_justification + 1) % len(JUSTIFICATIONS)
		log.info(f"Changing justification to {JUSTIFICATIONS[self.current_justification]}")
		self._target.set_justification(JUSTIFICATIONS[self.current_justification])
	
	def _update_direction(self) -> None:
		self.current_direction = (self.current_direction + 1) % len(DIRECTIONS)
		log.info(f"Changing direction to {DIRECTIONS[self.current_direction]}")
		self._target.set_direction(DIRECTIONS[self.current_direction])

	def _update_gap(self, value: float) -> None:
		self._target.set_gap(value)

	def handle_event(self, event: pygame.event.Event) -> None:
		pass

	def update(self, dt: float) -> None:
		self._target_wrapper.update(dt)
		self._tools.update(dt)

	def render(self, screen: pygame.Surface) -> None:
		screen.fill((255, 255, 255))

		self._target_wrapper.render(screen)
		self._tools.render(screen)

		pygame.display.flip()

	@classmethod
	def get_name(cls) -> str:
		return "test_zone"
	
	@override
	def on_enter(self) -> None:
		pass

	@override
	def on_exit(self) -> None:
		self._target_wrapper.on_scene_exit()
		self._tools.on_scene_exit()
