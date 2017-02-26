from pygame.locals import *
import pygame
import time
from Snake import Snake
from Food import Food
import random
from math import sqrt
from math import floor
import operator
from Neuron import visitedNeurons
import sys

def checkCollision(step, x1, y1, x2, y2):
	if x1 >= x2 and x1 < x2 + step and y1 >= y2 and y1 < y2 + step:
		return True

	return False

def getDistance(x1, y1, x2, y2):
	return sqrt((x1 - x2)*(x1 - x2) + (y1 - y2)*(y1 - y2))

class Game:
	WIDTH = 984
	HEIGHT = 984
	STEP = 24
	MAX_SNAKES = 20 # make sure it's even
	MAX_FOOD = 20
	MAX_LOOPS_PER_RUN = 500
	TIME_SLEEP = 0.001
	MAX_COORD = WIDTH / STEP - 1
	INITIAL_LENGTH = 4

	run = 1
	start_time = 0
	min_fitness = 100
	mean_fitness = 0
	overall_min_fitness = 100

	snakes_array = []
	food_array = []

	loop = 0

	def __init__(self):
		self._running = True
		self._display_surf = None
		self._snake_surf = None
		self._food_surf = None
		self._start_time = time.time()

		for i in range(self.MAX_SNAKES):
			self.snakes_array.append(Snake(self.INITIAL_LENGTH, self.STEP, i + 1))
		self.liveSnakes = self.MAX_SNAKES

		for i in range(self.MAX_FOOD):
			self.food_array.append(Food(self.STEP, random.randint(0, self.MAX_COORD), random.randint(0, self.MAX_COORD)))


	def on_init(self):
		pygame.init()
		self._display_surf = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.HWSURFACE)

		pygame.display.set_caption('Snake Learning AI')
		self._running = True
		self._snake_surf = pygame.image.load("../assets/block.png").convert()
		self._food_surf = pygame.image.load("../assets/food.png").convert()

	def on_event(self, event):
		if event.type == QUIT:
			self._running = False

	def on_loop(self):
		self.loop += 1
		for snake in self.snakes_array:
			if self.liveSnakes <= 0:
				self.resetLevel()

			if snake.isDead == True:
				continue

			snake.update()

			idxMinDistance = 0
			minDistance = self.WIDTH
			i = 0
			for food in self.food_array:
				dist = getDistance(snake.x[0], snake.y[0], food.x, food.y)
				if dist < minDistance:
					idxMinDistance = i
					minDistance = dist
				i += 1

				if checkCollision(self.STEP, snake.x[0], snake.y[0], food.x, food.y):
					# Found food
					snake.foundFood()
					food.rellocate(random.randint(0, self.MAX_COORD), random.randint(0, self.MAX_COORD))
					#print("Got food! - Food Count:", snake.foodCount)

			snake.setInputValues(self.food_array[idxMinDistance].x, self.food_array[idxMinDistance].y)

			# Wall collision
			if snake.x[0] > self.WIDTH or snake.x[0] < 0 or snake.y[0] > self.HEIGHT or snake.y[0] < 0:
				snake.isDead = True
				self.liveSnakes -= 1
				snake.calcFitness(-1 + time.time()-self.start_time)
				self.mean_fitness += snake.fitness

				if snake.fitness < self.min_fitness:
					self.min_fitness = snake.fitness

				#print("Wall collision! - Food Count:", snake.foodCount, "/ Fitness:", snake.fitness)

			# Self collision
			if snake.collidedOnSelf() == True:
				snake.isDead = True
				self.liveSnakes -= 1
				snake.calcFitness(-3 + time.time()-self.start_time)
				self.mean_fitness += snake.fitness

				if snake.fitness < self.min_fitness:
					self.min_fitness = snake.fitness

				#print("Self collision! - Food Count:", snake.foodCount, "/ Fitness:", snake.fitness)

		if self.loop == self.MAX_LOOPS_PER_RUN:
			self.resetLevel()

	def on_render(self):
		self._display_surf.fill((0, 0, 0))
		for snake in self.snakes_array:
			snake.draw(self._display_surf, self._snake_surf)
		for f in self.food_array:
			f.draw(self._display_surf, self._food_surf)

		pygame.display.flip()

		#print("Live snakes: ", self.liveSnakes)

	def on_cleanup(self):
		print("")
		print("Elapsed time:", time.time() - self._start_time, "seconds.")
		print("")
		pygame.display.quit()
		pygame.quit()

	def on_execute(self):
		if self.on_init() == False:
			self._running = False

		self.start_time = time.time()
		while self._running:
			pygame.event.pump()
			keys = pygame.key.get_pressed()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self._running = False
					self.on_cleanup()
					return
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						self._running = False
						self.on_cleanup()
					"""
					if event.key == pygame.K_RIGHT:
						for snake in self.snakes_array:
							snake.turn(dir = 0)
					elif event.key == pygame.K_LEFT:
						for snake in self.snakes_array:
							snake.turn(dir = 1)
					"""

			self.on_loop()
			self.on_render()

			time.sleep( self.TIME_SLEEP )

	def resetLevel(self):
		fitness = {}
		for idx, snake in enumerate(self.snakes_array):
			if snake.isDead == False:
				snake.calcFitness(time.time()-self.start_time)
				if self.min_fitness > snake.fitness:
					self.min_fitness = snake.fitness
					self.mean_fitness += snake.fitness

			fitness[idx] = snake.fitness

		fitness = sorted(fitness.items(), key=operator.itemgetter(1))
		new_list = []
		for i in range(self.MAX_SNAKES):
			idx = fitness[i][0]
			new_list.append(self.snakes_array[idx])

		N = floor(self.MAX_SNAKES / 2)
		if N == 0:
			N = 1
		for i in range(N):
			goodBoy = new_list[i]
			if self.MAX_SNAKES > 1:
				badBoy = new_list[i + N]
				badBoy.setSnakeNetwork(goodBoy.getSnakeNetwork().copy())
			goodBoy.getSnakeNetwork().mutateChangeWeights()
			goodBoy.getSnakeNetwork().mutate()

		for snake in self.snakes_array:
			snake.reset()

		self.mean_fitness /= self.MAX_SNAKES
		if self.overall_min_fitness >= self.min_fitness:
			self.overall_min_fitness = self.min_fitness

		print("")
		print("Resetting level...")
		print("Gen", self.run, "info:")
		print("Time elapsed:", time.time() - self.start_time, "seconds")
		print("Min fitness gen: ", self.min_fitness, "/ Mean fitness: ", self.mean_fitness)
		print("Overall Min Fitness:", self.overall_min_fitness)
		print("")

		visitedNeurons.clear()
		self.loop = 0
		self.liveSnakes = self.MAX_SNAKES
		self.run += 1
		self.min_fitness = 100
		self.mean_fitness = 0
		self.start_time = time.time()

