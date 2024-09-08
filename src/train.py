from gui import Container, Style, LabelElement
from gui.containers.flex_container import Alignment, Direction, FlexContainer
from scenes.level.player import Player
from scenes.level.camera import Camera
from core import IScene, app_state
from typing import override
import pygame
import pymunk
import neat
import neat.reporting
from random import random
import math
import pickle
from styles import SMALL_LABEL_STYLE
import util.logger as log


log.enable()
pygame.init()

app_state.set_window_size(1920 // 2, 1080 // 2)

screen = pygame.display.set_mode(app_state.get_window_size())

space = pymunk.Space()
space.gravity = (0, 0)
space.damping = 0.9

planet_data = app_state.get_planet_data(2)
player_data = app_state.get_player_data()

camera = Camera(40, 20)

gui = Container(width=app_state.get_width(), height=app_state.get_height()).with_children(
	FlexContainer(direction=Direction.COLUMN, align=Alignment.START, gap=10, top=10, left=10).with_children(
		gen_label := LabelElement("", style=SMALL_LABEL_STYLE),
		genome_label := LabelElement("", style=SMALL_LABEL_STYLE)
	)
)

class GUIReporter(neat.reporting.BaseReporter):
	def start_generation(self, generation):
		gen_label.set_text(f"Generation: {generation}")

config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
					 neat.DefaultSpeciesSet, neat.DefaultStagnation,
					 "data/stabilizer_config.ini")

ANGLE_TOLERANCE = math.radians(3)

def train_genome(genome: neat.DefaultGenome) -> float:
	net = neat.nn.FeedForwardNetwork.create(genome, config)

	player = Player(space, 0, 0, planet_data, player_data)
	player.set_angle(random() * 2 * math.pi)
	player.set_angular_velocity(random() * 30 - 15)
	camera.follow_object(player)

	time = 0.0
	score = 0.0

	average_velocity = 0.0

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				quit()

		dt = 1 / 60
		time += dt

		if time >= 15:
			return score - abs(average_velocity) * 0.01

		angle = player.get_angle()
		angle_vel = player.get_angular_velocity()

		output = net.activate((angle, angle_vel))
		acceleration = output[0]

		player.apply_rotation(acceleration)

		space.step(dt)

		camera.update(dt)
		gui.update(dt)

		average_velocity += player.get_angular_velocity()

		if abs((player.get_angle() + math.pi) % (2 * math.pi) - math.pi) < ANGLE_TOLERANCE:
			score += dt

		# Draw
		screen.fill((0, 0, 0))
		player.render(screen, camera)
		gui.render(screen)
		pygame.display.flip()


def eval_genomes(genomes: list[tuple[int, neat.DefaultGenome]], _) -> None:
	for genome_id, genome in genomes:
		genome_label.set_text(f"Genome: {genome_id}")
		genome.fitness = train_genome(genome)


# population = neat.Population(config)
population = neat.Checkpointer.restore_checkpoint("data/checkpoints/stabilizer-checkpoint-15")
population.add_reporter(neat.StdOutReporter(True))
stats = neat.StatisticsReporter()
population.add_reporter(stats)
population.add_reporter(neat.Checkpointer(5, filename_prefix="data/checkpoints/stabilizer-checkpoint-"))
population.add_reporter(GUIReporter())

winner = population.run(eval_genomes, 50)

# Save the winner.
with open("data/stabilizer.pkl", "wb") as f:
	pickle.dump(winner, f)

pygame.quit()
