from __future__ import annotations
import pygame
from dataclasses import dataclass
from typing import Optional
import util.asset_manager as am


@dataclass
class Style:
    text_color: Optional[tuple[int, int, int]] = None
    text_opacity: Optional[float] = None
    font: Optional[pygame.font.Font] = None
    background_color: Optional[tuple[int, int, int]] = None
    background_opacity: Optional[float] = None
    border_color: Optional[tuple[int, int, int]] = None
    border_opacity: Optional[float] = None
    border_width: Optional[int] = None
    border_radius: Optional[int] = None
    padding_x: Optional[int] = None
    padding_y: Optional[int] = None
    image_darken: Optional[float] = None
    image_rotation: Optional[float] = None

    def update(self, update_style: Style) -> Style:
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
        updated_style.image_darken = update_style.image_darken if update_style.image_darken is not None else self.image_darken
        updated_style.image_rotation = update_style.image_rotation if update_style.image_rotation is not None else self.image_rotation

        return updated_style
    
    def parent_update(self, parent_style: Style) -> Style:
        updated_style = Style()
        
        updated_style.text_color = parent_style.text_color if parent_style.text_color is not None else self.text_color
        updated_style.text_opacity = parent_style.text_opacity if parent_style.text_opacity is not None else self.text_opacity
        updated_style.font = parent_style.font if parent_style.font is not None else self.font
        updated_style.background_color = self.background_color
        updated_style.background_opacity = self.background_opacity
        updated_style.border_color = self.border_color
        updated_style.border_opacity = self.border_opacity
        updated_style.border_width = self.border_width
        updated_style.border_radius = self.border_radius
        updated_style.padding_x = self.padding_x
        updated_style.padding_y = self.padding_y
        updated_style.image_darken = self.image_darken
        updated_style.image_rotation = self.image_rotation

        return updated_style

        

DEFAULT_STYLE = Style(
	text_color=(255, 255, 255),
    text_opacity=1,
	font=am.get_font(),
	background_color=(0, 0, 0),
    background_opacity=0,
	border_color=(0, 0, 0),
    border_opacity=0,
	border_width=0,
	border_radius=0,
	padding_x=0,
	padding_y=0,
    image_darken=0,
    image_rotation=0,
)