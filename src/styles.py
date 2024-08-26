import pygame
from gui import Style
import util.asset_manager as am

COLOR_WINE = (96, 41, 62)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (255, 0, 0)


BUTTON_STYLE = Style(
	text_color=COLOR_WHITE,
	font=am.get_font("assets/font/Comfortaa-Regular.ttf", 20),
	background_color=COLOR_WINE,
	background_opacity=0.6,
	border_color=COLOR_WHITE,
	border_opacity=1,
	border_width=3,
	border_radius=10,
	padding_x=10,
	padding_y=5
)

BUTTON_STYLE_HOVERED = Style(
	text_color=COLOR_BLACK,
	background_color=COLOR_WHITE,
)

BUTTON_STYLE_PRESSED = Style(
	text_color=COLOR_BLACK,
	background_color=COLOR_WHITE,
	background_opacity=1,
)

HEADER_STYLE = Style(
	text_color=COLOR_WHITE,
	font=am.get_font("assets/font/Comfortaa-Bold.ttf", 30),
)

LABEL_STYLE = Style(
	text_color=COLOR_WHITE,
	font=am.get_font("assets/font/Comfortaa-Regular.ttf", 30),
)