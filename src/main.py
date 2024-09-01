import sys

import pygame
from core import App, app_state
from scenes import *
from scenes.level.physics_test import PhysicsTestScene
import util.logger as log


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
		app_state.register_scene(PhysicsTestScene)
    
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