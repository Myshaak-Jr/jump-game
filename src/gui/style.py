from __future__ import annotations
from dataclasses import dataclass, fields
from copy import copy


__all__ = [
	"Style",
	"FullStyle",
	"AnyStyle",
	"DEFAULT_STYLE"
]


type AnyStyle = Style | FullStyle

def _updated[T: AnyStyle](original: T, update: AnyStyle | None) -> T:
	updated = copy(original)

	if update is None:
		return updated
	
	for field in fields(original):
		attr = getattr(update, field.name)
		if attr is not None:
			setattr(updated, field.name, attr)
	
	return updated

def _parent_updated[T: AnyStyle](original: T, parent: AnyStyle | None) -> T:
	updated = copy(original)

	if parent is None:
		return updated
	
	if parent.text_color is not None:
		updated.text_color = parent.text_color
	if parent.text_opacity is not None:
		updated.text_opacity = parent.text_opacity
	if parent.font is not None:
		updated.font = parent.font
	if parent.font_size is not None:
		updated.font_size = parent.font_size
	if parent.bold is not None:
		updated.bold = parent.bold
	
	return updated


@dataclass
class Style:
	text_color: tuple[int, int, int] | None = None
	text_opacity: float | None = None
	font: str | None = None
	font_size: int | None = None
	bold: bool | None = None
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

	def updated(self, update_style: AnyStyle | None) -> Style:
		return _updated(self, update_style)
	
	def parent_updated(self, parent_style: AnyStyle | None) -> Style:
		return _parent_updated(self, parent_style)

@dataclass
class FullStyle:
	text_color: tuple[int, int, int]
	text_opacity: float
	font: str
	font_size: int
	bold: bool
	background_color: tuple[int, int, int]
	background_opacity: float
	border_color: tuple[int, int, int]
	border_opacity: float
	border_width: int
	border_radius: int
	padding_x: int
	padding_y: int
	image_darken: float
	image_rotation: float
	image_scale: float
	slider_track_color: tuple[int, int, int]
	slider_track_opacity: float
	slider_track_width: int
	slider_handle_color: tuple[int, int, int]
	slider_handle_radius: int
	slider_handle_border_color: tuple[int, int, int]
	slider_handle_border_width: int

	def updated(self, update_style: AnyStyle | None) -> FullStyle:
		return _updated(self, update_style)
	
	def parent_updated(self, parent_style: AnyStyle | None) -> FullStyle:
		return _parent_updated(self, parent_style)


DEFAULT_STYLE = FullStyle(
	text_color=(0, 0, 0),
	text_opacity=1,
	font="default",
	font_size=12,
	bold=False,
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