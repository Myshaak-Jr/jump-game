from gui import Style
import util.asset_manager as am

COLOR_WINE = (96, 41, 62)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (255, 0, 0)


BUTTON_STYLE = Style(
	text_color=COLOR_WHITE,
	font=am.get_font("assets/font/Comfortaa-Regular.ttf", 35),
	background_color=COLOR_WINE,
	background_opacity=0.6,
	border_color=COLOR_WINE,
	border_opacity=1,
	border_width=3,
	border_radius=10,
	padding_x=20,
	padding_y=10
)

BUTTON_STYLE_HOVERED = Style(
	border_color=COLOR_WHITE,
)

BUTTON_STYLE_PRESSED = Style(
	border_color=COLOR_WHITE,
	background_color=COLOR_WHITE,
)

HEADER_STYLE = Style(
	text_color=COLOR_WHITE,
	font=am.get_font("assets/font/Comfortaa-Bold.ttf", 50),
)

LABEL_STYLE = Style(
	text_color=COLOR_WHITE,
	font=am.get_font("assets/font/Comfortaa-Regular.ttf", 20),
)

DEBUG_STYLE = Style(
	border_color=COLOR_RED,
	border_width=1,
	border_opacity=1,
)
