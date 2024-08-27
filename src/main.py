import sys
from core import App, app_state
from scenes.main_menu import MainMenuScene
from scenes.level_scene import LevelScene
from scenes.game_over_scene import GameOverScene
import util.logger as log


def main() -> int:
	app_state.set_window_size(1920 // 2, 1080 // 2)
	app_state.register_scene(MainMenuScene)
	app_state.register_scene(LevelScene)
	app_state.register_scene(GameOverScene)

	app = App()
	app.set_scene(MainMenuScene())
	app.run()

	try:
		...
	except Exception as e:
		log.error(e)
		return 1
	return 0

if __name__ == '__main__':
	sys.exit(main())