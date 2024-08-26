from .scene import IScene


class AppState:
	def __init__(self, width: int, height: int) -> None:
		self._width = width
		self._height = height
		self._next_scene: IScene = None
		self._running = False

	@property
	def width(self) -> int:
		return self._width
	
	@width.setter
	def width(self, value: int) -> None:
		self._width = value
		
	@property
	def height(self) -> int:
		return self._height

	@height.setter
	def height(self, value: int) -> None:
		self._height = value

	def queue_scene(self, scene: IScene) -> None:
		self._next_scene = scene
	
	def queue_stop(self) -> None:
		self._running = False