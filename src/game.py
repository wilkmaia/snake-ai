import time
import operator
import math
import random
import sys

from pygame.locals import *
import pygame

import json

from snake import Snake
from food import Food
from neuron import visitedNeurons
from neuron import Neuron
from synapse import Synapse
from network import Network

STEP = 5
CROSSOVER_BEST_PERCENT = 0.40  # Max = 0.50
SAVE_FILE = "network.txt"


def check_collision(x1, y1, x2, y2):
    if x2 <= x1 < x2 + STEP and y2 <= y1 < y2 + STEP:
        return True

    return False


def get_distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2)*(x1 - x2) + (y1 - y2)*(y1 - y2))


class Game:
    WIDTH = 855
    HEIGHT = 855
    MAX_SNAKES = 10  # make sure it's even
    MAX_FOOD = 30
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
        self._print_data = False
        self._load_data = False
        self.snakeMinFitness = 0

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
                    snake.nextFoodX = food.x
                    snake.nextFoodY = food.y

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
                snake.calc_fitness(15 - time.time()+self.startTime)
                self.meanFitness += snake.fitness

                if snake.fitness < self.minFitness:
                    self.minFitness = snake.fitness
                    self.snakeMinFitness = snake.snakeNumber

                # print("Wall collision! - Food Count:", snake.foodCount, "/ Fitness:", snake.fitness)

            # Self collision
            if snake.collided_on_self():
                snake.isDead = True
                self.liveSnakes -= 1
                snake.calc_fitness(20 - time.time()+self.startTime)
                self.meanFitness += snake.fitness

                if snake.fitness < self.minFitness:
                    self.minFitness = snake.fitness
                    self.snakeMinFitness = snake.snakeNumber

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
                    if event.key == pygame.K_q:
                        self._print_data = True
                    if event.key == pygame.K_l:
                        self._load_data = True
                        self.reset_level(forced=True)
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
                    self.snakeMinFitness = snake.snakeNumber
                    self.meanFitness += snake.fitness

            fitness[idx] = snake.fitness

        fitness = sorted(fitness.items(), key=operator.itemgetter(1))
        new_list = []
        for i in range(self.MAX_SNAKES):
            idx = fitness[i][0]
            new_list.append(self.snakeList[idx])

        # CROSSOVER ALGORITHM 2.0
        # THE <CROSSOVER_BEST_PERCENT>% BEST MEMBERS WILL BE KEPT UNTOUCHED
        # THEIR COPIES WILL MUTATE
        #
        # THE POPULATION WILL BE REFILLED WITH SPECIAL MUTATIONS OF SELECTED
        # MEMBERS ALONG THEM. LOWER FITNESS MEANS HIGHER CHANCE OF BEING PICKED
        n = math.floor(self.MAX_SNAKES * CROSSOVER_BEST_PERCENT)
        best_members = new_list[:n]
        max_ = 1 / best_members[0].fitness

        for i in range(n, 2*n):
            new_list[i].network = new_list[i-n].network.copy()
            new_list[i].network.mutate()

        for i in range(2*n, self.MAX_SNAKES):
            while True:
                good_snake = random.choice(best_members)
                if random.uniform(0, max_) < 1 / good_snake.fitness:
                    break
            new_list[i].network = good_snake.network.copy()
            new_list[i].network.mutate(delta=0.5)

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
        snake_most_pieces = 0
        single_food_count = 0
        for snake in self.snakeList:
            food_count += snake.foodCount
            if snake.foodCount > single_food_count:
                single_food_count = snake.foodCount
                snake_most_pieces = snake.snakeNumber
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
        print("Min fitness gen:", self.minFitness,
              "snake #{} / Mean fitness:".format(self.snakeMinFitness), self.meanFitness)
        print("Overall Min Fitness:", self.overallMinFitness)
        print("Max food pieces caught by single snake:", single_food_count,
              "snake #{}".format(snake_most_pieces))
        print("Total food pieces caught:", food_count)
        print("")

        if self._load_data:
            self._load_data = False
            f = open(SAVE_FILE, "r")
            data = json.load(f)
            f.close()

            self.load_network(data)

        if self._print_data:
            self._print_data = False
            data = new_list[0].print_network(run=self.run)
            f = open(SAVE_FILE, "w")
            json.dump(data, f, sort_keys=False, indent=4)
            f.close()
            print("Best network data printed to 'network.txt' file.")
            print("")

        visitedNeurons.clear()
        self.loop = 0
        self.liveSnakes = self.MAX_SNAKES
        self.run += 1
        self.minFitness = sys.float_info.max
        self.meanFitness = 0
        self.startTime = time.time()

        return

    def load_network(self, o):
        sensor_nodes = o["sensor_nodes"]
        hidden_nodes = o["hidden_nodes"]
        output_nodes = o["output_nodes"]
        self.run = int(o["generations"])
        network = Network()
        network.k = int(o["network"])
        network.EPSILON = float(o["epsilon"])
        network.MUTATION_RATE = float(o["mutation_rate"])

        synapses_visited = []
        network.actuatorList = []
        network.sensorList = []
        network.inputNodeList = []
        network.outputNodeList = []
        network.inputOutputNodeList = []

        neurons = []
        for n in sensor_nodes:
            _id = list(n.keys())[0]
            neuron = Neuron()
            neuron.k = int(_id)
            network.sensorList.append(neuron)
            network.inputNodeList.append(neuron)
            neurons.append(neuron)
        for n in output_nodes:
            _id = list(n.keys())[0]
            neuron = Neuron()
            neuron.k = int(_id)
            network.actuatorList.append(neuron)
            network.outputNodeList.append(neuron)
            neurons.append(neuron)
        for n in hidden_nodes:
            _id = list(n.keys())[0]
            neuron = Neuron()
            neuron.k = int(_id)
            network.inputOutputNodeList.append(neuron)
            neurons.append(neuron)

        # Sensor Nodes
        for n in sensor_nodes:
            _id = list(n.keys())[0]
            neuron = self.find_neuron(neurons, int(_id))

            for s in n[_id]["output_synapses"]:
                for key, val in s.items():
                    if key in synapses_visited or key == "other_end":
                        continue

                    other_end = self.find_neuron(neurons, int(s["other_end"]))
                    syn = Synapse(neuron,
                                  other_end,
                                  float(val))
                    syn.k = int(key)
                    synapses_visited.append(key)
                    neuron.outputList.append(syn)
                    other_end.inputList.append(syn)

        # Output Nodes
        for n in output_nodes:
            _id = list(n.keys())[0]
            neuron = self.find_neuron(neurons, int(_id))

            for s in n[_id]["input_synapses"]:
                for key, val in s.items():
                    if key in synapses_visited or key == "other_end":
                        continue

                    other_end = self.find_neuron(neurons, int(s["other_end"]))
                    syn = Synapse(other_end,
                                  neuron,
                                  float(val))
                    syn.k = int(key)
                    synapses_visited.append(key)
                    neuron.inputList.append(syn)
                    other_end.outputList.append(syn)

        # Hidden Nodes
        for n in hidden_nodes:
            _id = list(n.keys())[0]
            neuron = self.find_neuron(neurons, int(_id))

            for s in n[_id]["input_synapses"]:
                for key, val in s.items():
                    if key in synapses_visited or key == "other_end":
                        continue

                    other_end = self.find_neuron(neurons, int(s["other_end"]))
                    syn = Synapse(other_end,
                                  neuron,
                                  float(val))
                    syn.k = int(key)
                    synapses_visited.append(key)
                    neuron.inputList.append(syn)
                    other_end.outputList.append(syn)

            for s in n[_id]["output_synapses"]:
                for key, val in s.items():
                    if key in synapses_visited or key == "other_end":
                        continue

                    other_end = self.find_neuron(neurons, int(s["other_end"]))
                    syn = Synapse(neuron,
                                  other_end,
                                  float(val))
                    syn.k = int(key)
                    synapses_visited.append(key)
                    neuron.outputList.append(syn)
                    other_end.inputList.append(syn)

        for snake in self.snakeList:
            snake.network = network.copy()

        return

    @staticmethod
    def find_neuron(neurons, _id):
        for n in neurons:
            if n.k == _id:
                return n

        return None
