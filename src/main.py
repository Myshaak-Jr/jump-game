import sys
from core import App, app_state
from scenes import *

import util.logger as log
 

def main() -> int:
	app_state.set_window_size(1920 // 2, 1080 // 2)
	app_state.register_scene(MainMenuScene)
	app_state.register_scene(LevelScene)
	app_state.register_scene(GameOverScene)
	app_state.register_scene(PauseMenuScene)
	app_state.register_scene(WinMenuScene)
	app_state.register_scene(AudioSettingsScene)

	app = None
	app = App()
	app.run("main_menu")
	app.quit()
	try:
		...
	except Exception as e:
		log.error(e)
		if app:
			app.quit()
		return 1
	return 0

if __name__ == '__main__':
	sys.exit(main())