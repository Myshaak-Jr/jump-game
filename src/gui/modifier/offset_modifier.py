from ..base import ISingleModifier, GUIElement


__all__ = ['OffsetModifier']


class OffsetModifier(ISingleModifier):
	def __init__(self, target: GUIElement, offset_x: float, offset_y: float):
		super().__init__(target)
		self._offset_x = offset_x
		self._offset_y = offset_y

	def get_offset(self) -> tuple[float, float]:
		offset_x, offset_y = super().get_offset()
		return (offset_x or 0) + self._offset_x, (offset_y or 0) + self._offset_y
	
	def set_offset(self, offset_x: float, offset_y: float) -> None:
		self._offset_x = offset_x
		self._offset_y = offset_y