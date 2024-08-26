import sys
from core import App, AppState
from scenes.main_menu import MainMenuScene
import util.logger as log


def main() -> int:
	app_state = AppState(1920 // 2, 1080 // 2)
	app = App(app_state)
	app.set_scene(MainMenuScene(app_state))
	app.run()

	try:
		...
	except Exception as e:
		log.error(e)
		return 1
	return 0

if __name__ == '__main__':
	sys.exit(main())