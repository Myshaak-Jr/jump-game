from cgitb import text
from core import IScene, app_state
import pygame
from gui import Container, FlexContainer, Style, ButtonModifier, LabelElement, Alignment, Justification, Direction
from random import randint
from gui.elements.slider_element import SliderElement
import util.asset_manager as am
import util.logger as log


NUM_DUMMIES = 10

WIDTH: int
HEIGHT: int

MIN_DUMMY_WIDTH: int
MAX_DUMMY_WIDTH: int

MIN_DUMMY_HEIGHT: int
MAX_DUMMY_HEIGHT: int

MAX_GAP = 40

DUMMY_STYLE = Style(
	border_color=(255, 0, 0),
	border_width=2,
	border_opacity=1,
)

def _create_dummy():
	return Container(
		width=randint(MIN_DUMMY_WIDTH, MAX_DUMMY_WIDTH),
		height=randint(MIN_DUMMY_HEIGHT, MAX_DUMMY_HEIGHT),
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
		global WIDTH, HEIGHT, MIN_DUMMY_WIDTH, MAX_DUMMY_WIDTH, MIN_DUMMY_HEIGHT, MAX_DUMMY_HEIGHT
		WIDTH = app_state.width * 9 // 10
		HEIGHT = app_state.height * 9 // 10

		MAX_DUMMY_WIDTH = WIDTH // 9
		MAX_DUMMY_HEIGHT = HEIGHT // 9

		MIN_DUMMY_WIDTH = MAX_DUMMY_WIDTH // 2
		MIN_DUMMY_HEIGHT = MAX_DUMMY_HEIGHT // 2

		self.current_direction = 0
		self.current_alignment = 0
		self.current_justification = 0

		self._target = FlexContainer(
			WIDTH, HEIGHT,
			direction=DIRECTIONS[self.current_direction],
			align=ALIGNMENTS[self.current_alignment],
			justify=JUSTIFICATIONS[self.current_justification],
			style=DUMMY_STYLE
		).with_children(
			_create_dummy()
			for _ in range(NUM_DUMMIES)
		)

		self._target_wrapper = FlexContainer(app_state.width, app_state.height, justify=Justification.CENTER, align=Alignment.CENTER).with_children(
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

	def update(self, dt: float) -> None | IScene:
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