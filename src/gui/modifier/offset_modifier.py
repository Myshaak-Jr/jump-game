from ..base import ISingleModifier, IElement


class OffsetModifier(ISingleModifier):
	def __init__(self, target: IElement, offset_x: int, offset_y: int):
		super().__init__(target)
		self._offset_x = offset_x
		self._offset_y = offset_y

	def get_offset(self) -> tuple[int, int]:
		offset_x, offset_y = super().get_offset()
		return (offset_x or 0) + self._offset_x, (offset_y or 0) + self._offset_y
	
	def set_offset(self, offset_x: int, offset_y: int) -> None:
		self._offset_x = offset_x
		self._offset_y = offset_y