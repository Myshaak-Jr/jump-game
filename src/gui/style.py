from __future__ import annotations
import pygame
from dataclasses import dataclass
import util.asset_manager as am
from copy import copy


@dataclass
class Style:
	text_color: tuple[int, int, int] | None = None
	text_opacity: float | None = None
	font: pygame.font.Font | None = None
	background_color: tuple[int, int, int] | None = None
	background_opacity: float | None = None
	border_color: tuple[int, int, int] | None = None
	border_opacity: float | None = None
	border_width: int | None = None
	border_radius: int | None = None
	padding_x: int | None = None
	padding_y: int | None = None
	image_darken: float | None = None
	image_rotation: float | None = None
	image_scale: float | None = None
	slider_track_color: tuple[int, int, int] | None = None
	slider_track_opacity: float | None = None
	slider_track_width: int | None = None
	slider_handle_color: tuple[int, int, int] | None = None
	slider_handle_radius: int | None = None
	slider_handle_border_color: tuple[int, int, int] | None = None
	slider_handle_border_width: int | None = None

	def updated(self, update_style: Style) -> Style:
		updated_style = Style()
		
		updated_style.text_color = update_style.text_color if update_style.text_color is not None else self.text_color
		updated_style.text_opacity = update_style.text_opacity if update_style.text_opacity is not None else self.text_opacity
		updated_style.font = update_style.font if update_style.font is not None else self.font
		updated_style.background_color = update_style.background_color if update_style.background_color is not None else self.background_color
		updated_style.background_opacity = update_style.background_opacity if update_style.background_opacity is not None else self.background_opacity
		updated_style.border_color = update_style.border_color if update_style.border_color is not None else self.border_color
		updated_style.border_opacity = update_style.border_opacity if update_style.border_opacity is not None else self.border_opacity
		updated_style.border_width = update_style.border_width if update_style.border_width is not None else self.border_width
		updated_style.border_radius = update_style.border_radius if update_style.border_radius is not None else self.border_radius
		updated_style.padding_x = update_style.padding_x if update_style.padding_x is not None else self.padding_x
		updated_style.padding_y = update_style.padding_y if update_style.padding_y is not None else self.padding_y

		# Image properties
		updated_style.image_darken = update_style.image_darken if update_style.image_darken is not None else self.image_darken
		updated_style.image_rotation = (update_style.image_rotation or 0) + (self.image_rotation or 0)
		updated_style.image_scale = (update_style.image_scale if update_style.image_scale is not None else 1) * (self.image_scale if self.image_scale is not None else 1)

		# Slider properties
		updated_style.slider_track_color = update_style.slider_track_color if update_style.slider_track_color is not None else self.slider_track_color
		updated_style.slider_track_opacity = update_style.slider_track_opacity if update_style.slider_track_opacity is not None else self.slider_track_opacity
		updated_style.slider_track_width = update_style.slider_track_width if update_style.slider_track_width is not None else self.slider_track_width
		updated_style.slider_handle_color = update_style.slider_handle_color if update_style.slider_handle_color is not None else self.slider_handle_color
		updated_style.slider_handle_radius = update_style.slider_handle_radius if update_style.slider_handle_radius is not None else self.slider_handle_radius
		updated_style.slider_handle_border_color = update_style.slider_handle_border_color if update_style.slider_handle_border_color is not None else self.slider_handle_border_color
		updated_style.slider_handle_border_width = update_style.slider_handle_border_width if update_style.slider_handle_border_width is not None else self.slider_handle_border_width

		return updated_style
	
	def parent_updated(self, parent_style: Style) -> Style:
		updated_style = copy(self)
		
		updated_style.text_color = parent_style.text_color if parent_style.text_color is not None else self.text_color
		updated_style.text_opacity = parent_style.text_opacity if parent_style.text_opacity is not None else self.text_opacity
		updated_style.font = parent_style.font if parent_style.font is not None else self.font

		return updated_style


DEFAULT_STYLE = Style(
	text_color=(0, 0, 0),
	text_opacity=1,
	font=am.get_font(),
	background_color=(0, 0, 0),
	background_opacity=0,
	border_color=(0, 0, 0),
	border_opacity=0,
	border_width=0,
	border_radius=-1,
	padding_x=0,
	padding_y=0,
	# Image properties
	image_darken=0,
	image_rotation=0,
	image_scale=1,
	# Slider properties
	slider_track_color=(0, 0, 0),
	slider_track_opacity=1,
	slider_track_width=3,
	slider_handle_color=(0, 0, 0),
	slider_handle_radius=15,
	slider_handle_border_color=(0, 0, 0),
	slider_handle_border_width=3
)