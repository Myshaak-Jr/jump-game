import threading
import neat.math_util
import neat.six_util
from gui import Container, Style, LabelElement
from gui.containers.flex_container import Alignment, Direction, FlexContainer, Justification
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
from styles import LITTLE_LABEL_STYLE
import util.logger as log
import concurrent.futures
import time
import os


log.enable()
pygame.init()

#app_state.set_window_size(1500, 300)
#screen = pygame.display.set_mode(app_state.get_window_size())

registry_lock = threading.Lock()
worker_id_registry: dict[int, int] = {}
def get_id(id: int) -> int:
	with registry_lock:
		if id not in worker_id_registry:
			worker_id_registry[id] = len(worker_id_registry)
	return worker_id_registry[id]

def reset_ids() -> None:
	with registry_lock:
		worker_id_registry.clear()

planet_data = app_state.get_planet_data(2)
player_data = app_state.get_player_data()

max_workers = os.cpu_count() or 1

gui_lock = threading.Lock()
gui = Container(width=app_state.get_width(), height=app_state.get_height()).with_children(
	FlexContainer(direction=Direction.COLUMN, align=Alignment.START, gap=10, top=10, left=10).with_children(
		gen_label := LabelElement("", style=LITTLE_LABEL_STYLE),
		threads_info := FlexContainer(min_width=app_state.get_width(), justify=Justification.CENTER, gap=10).with_children(
			FlexContainer(direction=Direction.COLUMN, align=Alignment.START, gap=5).with_children(
				FlexContainer(direction=Direction.ROW, justify=Justification.SPACE_BETWEEN, gap=5).with_children(
					LabelElement("Thread ID:", style=LITTLE_LABEL_STYLE),
					LabelElement("", style=LITTLE_LABEL_STYLE),
				),
				FlexContainer(direction=Direction.ROW, justify=Justification.SPACE_BETWEEN, gap=5).with_children(
					LabelElement("Genome ID:", style=LITTLE_LABEL_STYLE),
					LabelElement("", style=LITTLE_LABEL_STYLE),
				),
				FlexContainer(direction=Direction.ROW, justify=Justification.SPACE_BETWEEN, gap=5).with_children(
					LabelElement("Last Fitness:", style=LITTLE_LABEL_STYLE),
					LabelElement("", style=LITTLE_LABEL_STYLE)
				)
			)
			for _ in range(max_workers)
		)
	),
)

gui.update(0)

class LogReporter(neat.reporting.BaseReporter):
	"""Uses `log.info` to output information about the run; an example reporter class."""
	def __init__(self, show_species_detail):
		self.show_species_detail = show_species_detail
		self.generation = None
		self.generation_start_time = None
		self.generation_times = []
		self.num_extinctions = 0

	def start_generation(self, generation):
		self.generation = generation
		log.info('\n ****** Running generation {0} ****** \n'.format(generation))
		self.generation_start_time = time.time()

	def end_generation(self, config, population, species_set):
		ng = len(population)
		ns = len(species_set.species)
		if self.show_species_detail:
			log.info('Population of {0:d} members in {1:d} species:'.format(ng, ns))
			sids = list(neat.six_util.iterkeys(species_set.species))
			sids.sort()
			log.info("   ID   age  size  fitness  adj fit  stag")
			log.info("  ====  ===  ====  =======  =======  ====")
			for sid in sids:
				s = species_set.species[sid]
				a = self.generation - s.created
				n = len(s.members)
				f = "--" if s.fitness is None else "{:.1f}".format(s.fitness)
				af = "--" if s.adjusted_fitness is None else "{:.3f}".format(s.adjusted_fitness)
				st = self.generation - s.last_improved
				log.info(
					"  {: >4}  {: >3}  {: >4}  {: >7}  {: >7}  {: >4}".format(sid, a, n, f, af, st))
		else:
			log.info('Population of {0:d} members in {1:d} species'.format(ng, ns))

		elapsed = 0
		if self.generation_start_time:
			elapsed = time.time() - self.generation_start_time
		self.generation_times.append(elapsed)
		self.generation_times = self.generation_times[-10:]
		average = sum(self.generation_times) / len(self.generation_times)
		log.info('Total extinctions: {0:d}'.format(self.num_extinctions))
		if len(self.generation_times) > 1:
			log.info("Generation time: {0:.3f} sec ({1:.3f} average)".format(elapsed, average))
		else:
			log.info("Generation time: {0:.3f} sec".format(elapsed))

	def post_evaluate(self, config, population, species, best_genome):
		# pylint: disable=no-self-use
		fitnesses = [c.fitness for c in neat.six_util.itervalues(population)]
		fit_mean = neat.math_util.mean(fitnesses)
		fit_std = neat.math_util.stdev(fitnesses)
		best_species_id = species.get_species_id(best_genome.key)
		log.info('Population\'s average fitness: {0:3.5f} stdev: {1:3.5f}'.format(fit_mean, fit_std))
		log.info(
			'Best fitness: {0:3.5f} - size: {1!r} - species {2} - id {3}'.format(best_genome.fitness,
																				 best_genome.size(),
																				 best_species_id,
																				 best_genome.key))

	def complete_extinction(self):
		self.num_extinctions += 1
		log.info('All species extinct.')

	def found_solution(self, config, generation, best):
		log.info('\nBest individual in generation {0} meets fitness threshold - complexity: {1!r}'.format(
			self.generation, best.size()))

	def species_stagnant(self, sid, species):
		if self.show_species_detail:
			log.info("\nSpecies {0} with {1} members is stagnated: removing it".format(sid, len(species.members)))

	def info(self, msg):
		log.info(msg)

class GUIReporter(neat.reporting.BaseReporter):
	def start_generation(self, generation):
		with gui_lock:
			gen_label.set_text(f"Generation: {generation}")

config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
					 neat.DefaultSpeciesSet, neat.DefaultStagnation,
					 "data/stabilizer_config.ini")

ANGLE_TOLERANCE = math.radians(3)

def train_genome(genome_id: int, genome: neat.DefaultGenome) -> float:
	worker_id = get_id(threading.get_ident())
	# with gui_lock:
	# 	containers = [x.get_children()[1] for x in threads_info.get_children()[worker_id].get_children()]
	# 	containers[0].set_text(str(worker_id))
	# 	containers[1].set_text(str(genome_id))
	# 	gui.render(screen)

	net = neat.nn.FeedForwardNetwork.create(genome, config)

	space = pymunk.Space()
	space.gravity = (0, 0)
	space.damping = 0.9

	player = Player(space, 0, 0, planet_data, player_data, physics_only = True)
	player.set_angle(random() * 2 * math.pi)
	if (random() < 0.5):
		player.set_angular_velocity(-10)
	else:
		player.set_angular_velocity(10)

	time = 0.0
	score = 0.0

	while True:
		dt = 1 / 60
		time += dt

		if time >= 15:
			final_velocity = player.get_angular_velocity()
			if abs(final_velocity) < 0.5:
				score += 1 / (1 + abs(final_velocity)) * 10
			# with gui_lock:
			# 	containers[2].set_text(f"{score:.2f}")
			# 	gui.render(screen)
			return score

		angle = player.get_normalized_angle()
		angle_vel = player.get_angular_velocity()

		output = net.activate((angle, angle_vel))
		acceleration = output[0]

		player.apply_rotation(acceleration)

		space.step(dt)

		if abs(player.get_normalized_angle()) < ANGLE_TOLERANCE:
			score += dt

def eval_genomes(genomes: list[tuple[int, neat.DefaultGenome]], _) -> None:
	reset_ids()
	with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
		futures = [executor.submit(train_genome, genome_id, genome) for genome_id, genome in genomes]
		for future, (genome_id, genome) in zip(futures, genomes):
			genome.fitness = future.result()

def train() -> None:
	population = neat.Population(config)
	# population = neat.Checkpointer.restore_checkpoint("data/checkpoints/stabilizer-checkpoint-49")
	population.add_reporter(LogReporter(True))
	stats = neat.StatisticsReporter()
	population.add_reporter(stats)
	population.add_reporter(neat.Checkpointer(5, filename_prefix="data/checkpoints/stabilizer-checkpoint-"))
	population.add_reporter(GUIReporter())

	winner = population.run(eval_genomes, 50)

	# Save the winner.
	with open("data/stabilizer.pkl", "wb") as f:
		pickle.dump(winner, f)

def test() -> None:
	# load net
	with open("data/stabilizer-first.pkl", "rb") as f:
		winner = pickle.load(f)
	
	app_state.set_window_size(800, 800)
	screen = pygame.display.set_mode(app_state.get_window_size())
	pygame.display.set_caption("Stabilizer Test")

	space = pymunk.Space()
	space.gravity = (0, 0)
	space.damping = 0.9
	player = Player(space, 0, 0, planet_data, player_data)
	net = neat.nn.FeedForwardNetwork.create(winner, config)

	clock = pygame.time.Clock()

	camera = Camera(30, 15)
	camera.follow_object(player)

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				return

		dt = clock.tick() / 1000

		key_state = pygame.key.get_pressed()
		if key_state[pygame.K_q]:
			player.set_angular_velocity(-10)
		if key_state[pygame.K_e]:
			player.set_angular_velocity(10)

		angle = player.get_normalized_angle()
		angle_vel = player.get_angular_velocity()

		output = net.activate((angle, angle_vel))
		acceleration = output[0] * 100

		player.apply_rotation(acceleration)

		space.step(dt)
		camera.update(dt)

		screen.fill((0, 0, 0))
		player.render(screen, camera)
		pygame.display.flip()


def test_differential_approach():
	app_state.set_window_size(800, 800)
	screen = pygame.display.set_mode(app_state.get_window_size())
	pygame.display.set_caption("Stabilizer Test")

	space = pymunk.Space()
	space.gravity = (0, 0)
	space.damping = 0.9
	player = Player(space, 0, 0, planet_data, player_data)

	clock = pygame.time.Clock()

	camera = Camera(30, 15)
	camera.follow_object(player)

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				return

		dt = clock.tick() / 1000

		key_state = pygame.key.get_pressed()
		if key_state[pygame.K_q]:
			player.set_angular_velocity(-10)
		if key_state[pygame.K_e]:
			player.set_angular_velocity(10)

		angle = player.get_normalized_angle()
		angle_vel = player.get_angular_velocity()

		Kp = 50
		Kd = 10

		accel = Kp * angle + Kd * angle_vel

		player.apply_rotation(accel)

		space.step(dt)
		camera.update(dt)

		screen.fill((0, 0, 0))
		player.render(screen, camera)
		pygame.display.flip()



pygame.quit()

if __name__ == "__main__":
	# train()
	test_differential_approach()