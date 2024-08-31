import sys

import pygame
from core import App, app_state
from scenes import *
import util.logger as log


def main() -> int:
	log.enable()
	app_state.enable_fps()
	app_state.register_scene(MainMenuScene)
	app_state.register_scene(GameOverScene)
	app_state.register_scene(PauseMenuScene)
	app_state.register_scene(WinMenuScene)
	app_state.register_scene(AudioSettingsScene)
	app_state.register_scene(LevelScene)

	app = None
	app = App()
	
	info = pygame.display.Info()
	app_state.set_window_size(info.current_w // 2, info.current_h // 2)
	pygame.display.set_window_position((info.current_w // 4, info.current_h // 4)) 

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