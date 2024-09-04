import sys

import pygame
from core import App, app_state
from scenes import *
import util.logger as log


"""
TODO: Fix the background not being drawn at the correct position
TODO: Add music and sounds
TODO: Add settings menuaaa
TODO: Add more levels
TODO: Add level select menu
TODO: Fix wrong clipping of the tiles
TODO: Add gui caching
"""


def main() -> int:
	app = None

	try:
		log.enable()
		app_state.enable_fps()
		app_state.register_scene(MainMenuScene)
		app_state.register_scene(GameOverScene)
		app_state.register_scene(PauseMenuScene)
		app_state.register_scene(WinMenuScene)
		app_state.register_scene(AudioSettingsScene)
		app_state.register_scene(LevelScene)
    
		app = App()
		 
		info = pygame.display.Info()
		app_state.set_window_size(1920 // 2, 1080 // 2)
		pygame.display.set_window_position((info.current_w // 4, info.current_h // 4)) 

		app.run("main_menu")

	except Exception as e:
		log.error(e)

	if app is not None:
		app.quit()

	return 0

if __name__ == '__main__':
	sys.exit(main())