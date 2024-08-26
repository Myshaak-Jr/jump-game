from __future__ import annotations
import pygame
from dataclasses import dataclass, fields
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

    def update(self, update_style: Style) -> Style:
        """Creates a copy of self updated with non-None members of update_style"""
        # Create a new instance of Style to hold updated values
        updated_style = Style()
        
        # Iterate over each field in the dataclass
        for field in fields(self):
            field_name = field.name
            current_value = getattr(self, field_name)
            new_value = getattr(update_style, field_name)
            
            # Set the updated value in the new instance
            setattr(updated_style, field_name, new_value if new_value is not None else current_value)
        
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
	padding_y=0
)