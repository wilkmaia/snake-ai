import time
import operator
import math
import random
import sys

from pygame.locals import *
import pygame

from snake import Snake
from food import Food
from neuron import visitedNeurons

STEP = 12


def check_collision(x1, y1, x2, y2):
    if x2 <= x1 < x2 + STEP and y2 <= y1 < y2 + STEP:
        return True

    return False


def get_distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2)*(x1 - x2) + (y1 - y2)*(y1 - y2))


class Game:
    WIDTH = 984
    HEIGHT = 984
    MAX_SNAKES = 50  # make sure it's even
    MAX_FOOD = 20
    MAX_LOOPS_PER_RUN = 2500
    TIME_SLEEP = 0.001
    MAX_COORD = WIDTH / STEP - 1
    INITIAL_LENGTH = 3

    run = 1
    startTime = 0
    minFitness = sys.float_info.max
    meanFitness = 0
    overallMinFitness = sys.float_info.max

    snakeList = []
    foodList = []

    loop = 0

    def __init__(self):
        self._running = True
        self._displaySurf = None
        self._snakeSurf = None
        self._foodSurf = None
        self._startTime = time.time()
        self._display = True
        self._paused = False

        self.liveSnakes = self.MAX_SNAKES
        for i in range(self.MAX_SNAKES):
            snake = Snake(random.randint(0, self.MAX_COORD),
                          random.randint(0, self.MAX_COORD),
                          self.INITIAL_LENGTH, i+1)
            self.snakeList.append(snake)

        for i in range(self.MAX_FOOD):
            food_piece = Food(random.randint(0, self.MAX_COORD),
                              random.randint(0, self.MAX_COORD))
            self.foodList.append(food_piece)

    def on_init(self):
        pygame.init()
        self._displaySurf = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.HWSURFACE)

        pygame.display.set_caption('Snake Learning AI')
        self._running = True
        self._snakeSurf = pygame.image.load("../assets/block.png").convert()
        self._foodSurf = pygame.image.load("../assets/food.png").convert()

        return True

    def on_event(self, event):
        if event.type == QUIT:
            self._running = False

    def on_loop(self):
        self.loop += 1

        if self.liveSnakes <= 0:
                self.reset_level()

        for snake in self.snakeList:
            if snake.isDead:
                continue

            snake.update()

            idx_min_distance = 1
            min_distance = self.WIDTH
            i = 0
            for food in self.foodList:
                i += 1
                if not food.available:
                    continue

                dist = get_distance(snake.x[0], snake.y[0], food.x, food.y)
                if dist < min_distance:
                    idx_min_distance = i
                    min_distance = dist

                if check_collision(snake.x[0], snake.y[0], food.x, food.y):
                    # Found food
                    snake.found_food()
                    food.relocate(random.randint(0, self.MAX_COORD),
                                  random.randint(0, self.MAX_COORD))
                    # food.available = False
                    # print("Got food! - Food Count:", snake.foodCount)

            snake.set_input_values(self.foodList[idx_min_distance - 1].x / STEP,
                                   self.foodList[idx_min_distance - 1].y / STEP)

            # Wall collision
            if (snake.x[0] >= self.WIDTH
                    or snake.x[0] < 0
                    or snake.y[0] >= self.HEIGHT
                    or snake.y[0] < 0):
                snake.isDead = True

                self.liveSnakes -= 1
                snake.calc_fitness(3 - time.time()-self.startTime)
                self.meanFitness += snake.fitness

                if snake.fitness < self.minFitness:
                    self.minFitness = snake.fitness

                # print("Wall collision! - Food Count:", snake.foodCount, "/ Fitness:", snake.fitness)

            # Self collision
            if snake.collided_on_self():
                snake.isDead = True
                self.liveSnakes -= 1
                snake.calc_fitness(5 - time.time()-self.startTime)
                self.meanFitness += snake.fitness

                if snake.fitness < self.minFitness:
                    self.minFitness = snake.fitness

                # print("Self collision! - Food Count:", snake.foodCount, "/ Fitness:", snake.fitness)

        if self.loop == self.MAX_LOOPS_PER_RUN:
            self.reset_level(forced=True)

    def on_render(self):
        self._displaySurf.fill((0, 0, 0))
        for snake in self.snakeList:
            snake.draw(self._displaySurf, self._snakeSurf)
        for f in self.foodList:
            f.draw(self._displaySurf, self._foodSurf)

        pygame.display.flip()

        # print("Live snakes: ", self.liveSnakes)

    def on_cleanup(self):
        print("")
        print("Elapsed time:", time.time() - self._startTime, "seconds.")
        print("")
        pygame.display.quit()
        pygame.quit()

    def on_execute(self):
        if not self.on_init():
            self._running = False

        self.startTime = time.time()
        while self._running:
            pygame.event.pump()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                    self.on_cleanup()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self._running = False
                        self.on_cleanup()
                    if event.key == pygame.K_p:
                        self._paused = not self._paused
                    if event.key == pygame.K_d:
                        self._display = not self._display
                    """
                    if event.key == pygame.K_RIGHT:
                        for snake in self.snakeList:
                            snake.turn(dir = 0)
                    elif event.key == pygame.K_LEFT:
                        for snake in self.snakeList:
                            snake.turn(dir = 1)
                    """

            if not self._paused:
                self.on_loop()

            if self._display:
                self.on_render()

            time.sleep(self.TIME_SLEEP)

    def reset_level(self, forced=False):
        fitness = {}
        for idx, snake in enumerate(self.snakeList):
            if not snake.isDead:
                snake.calc_fitness(-(time.time() - self.startTime))
                if self.minFitness > snake.fitness:
                    self.minFitness = snake.fitness
                    self.meanFitness += snake.fitness

            fitness[idx] = snake.fitness

        fitness = sorted(fitness.items(), key=operator.itemgetter(1))
        new_list = []
        for i in range(self.MAX_SNAKES):
            idx = fitness[i][0]
            new_list.append(self.snakeList[idx])

        # CROSSOVER ALGORITHM 2.0
        # THE WORST MEMBERS (50%) OF THE POPULATION WILL BE FORGOTTEN
        # THE BEST MEMBERS WILL MUTATE
        #
        # THE POPULATION WILL BE REFILLED BY MIMICKING GOOD MEMBERS BEFORE MUTATION
        # THE RATE OF A GOOD MEMBER BEING PICKED IS THE INVERSE OF ITS FITNESS
        n = math.floor(self.MAX_SNAKES * 0.5)
        best_members = new_list[:n]
        max_ = 1 / best_members[0].fitness

        start = self.MAX_SNAKES - n
        for i in range(start, self.MAX_SNAKES):
            while True:
                good_snake = random.choice(best_members)
                if random.uniform(0, max_) < 1 / good_snake.fitness:
                    break
            new_list[i].network = good_snake.network.copy()

        for snake in best_members:
            snake.network.mutate()

        # CROSSOVER ALGORITHM
        # THE BETTER MEMBERS (HALF) OF THE POPULATION MUTATE
        # BEFORE MUTATING THEIR NETWORK IS SENT TO THE WORST MEMBERS
        # n = math.floor(self.MAX_SNAKES / 2)
        # if n == 0:
        #     n = 1
        # for i in range(n):
        #     good_boy = new_list[i]
        #     if self.MAX_SNAKES > 1:
        #         bad_boy = new_list[i + n]
        #         bad_boy.network = good_boy.network.copy()
        #     # good_boy.network.mutate_change_weights()
        #     good_boy.network.mutate()

        food_count = 0
        single_food_count = 0
        for snake in self.snakeList:
            food_count += snake.foodCount
            if snake.foodCount > single_food_count:
                single_food_count = snake.foodCount
            snake.reset(random.randint(0, self.MAX_COORD), random.randint(0, self.MAX_COORD))

        for food in self.foodList:
            food.available = True
        #     food.relocate(random.randint(0, self.MAX_COORD), random.randint(0, self.MAX_COORD))

        self.meanFitness /= self.MAX_SNAKES
        if self.overallMinFitness >= self.minFitness:
            self.overallMinFitness = self.minFitness

        print("")
        print("Resetting level...")
        if forced:
            print("Forced reset!!!!")
        print("Gen", self.run, "info:")
        print("Time elapsed:", time.time() - self.startTime, "seconds")
        print("Min fitness gen: ", self.minFitness, "/ Mean fitness: ", self.meanFitness)
        print("Overall Min Fitness:", self.overallMinFitness)
        print("Max food pieces caught by single snake:", single_food_count)
        print("Total food pieces caught:", food_count)
        print("")

        visitedNeurons.clear()
        self.loop = 0
        self.liveSnakes = self.MAX_SNAKES
        self.run += 1
        self.minFitness = sys.float_info.max
        self.meanFitness = 0
        self.startTime = time.time()
