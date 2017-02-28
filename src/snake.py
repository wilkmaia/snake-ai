from enum import Enum
import math
import time

import game
from network import Network
from neuron import Neuron


class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


class Snake:
    PROP_CCW = 0.5
    PROP_CW = 0.6
    MUL = 1
    UPDATE_COUNT_MAX = 0
    NETWORK_MUTATE_RATE = 1
    NUMBER_OF_INPUTS = 8

    def __init__(self, x, y, length, snake_number):
        self.x = []
        self.y = []
        self.length = length
        self.snakeNumber = snake_number
        self.INITIAL_LENGTH = length
        self.INITIAL_X = x
        self.INITIAL_Y = y
        self.DIRECTION = Direction.RIGHT
        self.timeLastFood = time.time()

        for i in range(length):
            self.x.append(game.STEP * self.MUL * (x - i))
            self.y.append(game.STEP * self.MUL * y)

        self.inputX = 0
        self.inputY = 0
        self.inputDistanceTop = 0
        self.inputDistanceRight = 0
        self.inputDistanceBottom = 0
        self.inputDistanceLeft = 0
        self.lastMoves = [0, 0]
        self.forbiddenMove = (self.DIRECTION.value + 2) % 4
        self.inputNextTile = 0
        self.inputRightTile = 0
        self.inputLeftTile = 0

        self.network = Network(mut_rate=self.NETWORK_MUTATE_RATE)
        self.foodCount = 0
        self.groundCovered = 0
        self.isDead = False
        self.fitness = 0
        self.inputList = []
        self.updateCount = 0
        self.setup_network()

    # dir
    # 0 -> Clockwise
    # 1 -> Counterclockwise
    def turn(self, dir_=0):
        num_dir = len(list(Direction))

        next_dir_value = 0
        if dir_ == 0:
            next_dir_value = (self.DIRECTION.value+1) % num_dir
        elif dir_ == 1:
            if self.DIRECTION.value == 0:
                next_dir_value = 3
            else:
                next_dir_value = (self.DIRECTION.value-1)

        next_dir = Direction(next_dir_value)
        return self.get_next_x_y(dir_=next_dir)

    def update(self):
        if self.isDead:
            return

        self.updateCount += 1
        if self.updateCount >= self.UPDATE_COUNT_MAX:
            if len(self.inputList) > self.NUMBER_OF_INPUTS:
                self.inputList = self.inputList[:self.NUMBER_OF_INPUTS]
                self.network.sensorList = self.network.sensorList[:self.NUMBER_OF_INPUTS]

            self.network.set_input_values([
                self.inputX,
                self.inputY,
                self.inputDistanceTop,
                self.inputDistanceRight,
                self.inputDistanceBottom,
                self.inputDistanceLeft,
                # self.forbiddenMove,
                self.lastMoves[0],
                self.lastMoves[1],
                # self.lastMoves[2],
                # self.lastMoves[3]
            ])

            # TURN COUNTERCLOCKWISE OR CLOCKWISE
            # prop = self.network.propagate()
            # print("Snake #{} - prop: {}".format(self.snakeNumber, prop))
            # if prop <= self.PROP_CCW:
            #    self.turn(dir_=1)        # Turn Counterclockwise
            # elif prop >= self.PROP_CW:
            #     self.turn(dir_=0)        # Turn Clockwise

            # MOVE UP, RIGHT, DOWN OR LEFT
            prop = self.network.propagate()
            idx = prop.index(max(prop))
            next_dir = Direction(idx)
            if self.DIRECTION == Direction.UP and next_dir == Direction.DOWN:
                next_dir = Direction.UP
            elif self.DIRECTION == Direction.DOWN and next_dir == Direction.UP:
                next_dir = Direction.DOWN
            elif self.DIRECTION == Direction.LEFT and next_dir == Direction.RIGHT:
                next_dir = Direction.LEFT
            elif self.DIRECTION == Direction.RIGHT and next_dir == Direction.LEFT:
                next_dir = Direction.RIGHT
            self.DIRECTION = next_dir
            # self.forbiddenMove = (idx + 2) % 4

            # UPDATE LAST MOVES LIST
            self.lastMoves = self.lastMoves[1:]
            self.lastMoves.append(idx / 3)

            for i in range(self.length-1, 0, -1):
                self.x[i] = self.x[i-1]
                self.y[i] = self.y[i-1]

            self.x[0], self.y[0] = self.get_next_x_y()
            self.updateCount = 0

    def get_next_x_y(self, dir_=None):
        if dir_ is None:
            dir_ = self.DIRECTION
        x = self.x[0]
        y = self.y[0]
        if dir_ == Direction.UP:
            y -= game.STEP
        elif dir_ == Direction.RIGHT:
            x += game.STEP
        elif dir_ == Direction.DOWN:
            y += game.STEP
        elif dir_ == Direction.LEFT:
            x -= game.STEP
        return x, y

    def draw(self, surface, image):
        if self.isDead:
            return

        for i in range(self.length):
            surface.blit(image, (self.x[i], self.y[i]))

    def collided_on_self(self, x1=-1, y1=-1):
        if x1 == -1:
            x1 = self.x[0]
        if y1 == -1:
            y1 = self.y[0]
        for i in range(1, self.length):
            if game.check_collision(x1, y1, self.x[i], self.y[i]):
                return True

        return False

    def found_food(self):
        self.length += 1
        self.foodCount += 1
        self.timeLastFood = time.time()

        self.x.append(self.x[self.length - 2])
        self.y.append(self.y[self.length - 2])

    def setup_network(self):
        # Inputs
        # X and Y distances to the next food piece
        # Distances to the 4 walls
        # Last 2 moves
        self.inputList = [Neuron(), Neuron(), Neuron(), Neuron(), Neuron(),
                          Neuron(), Neuron(), Neuron()]

        self.network.sensorList = self.inputList
        self.network.inputNodeList = self.inputList

        # self.network.set_input_values([
        #     game.Game.WIDTH/game.STEP,
        #     game.Game.HEIGHT/game.STEP,
        #     0,                              # Distance to TOP wall
        #     game.Game.WIDTH/game.STEP,      # Distance to RIGHT wall
        #     game.Game.HEIGHT/game.STEP,     # Distance to BOTTOM wall
        #     game.STEP/game.STEP             # Distance do LEFT wall
        # ])

    # (x, y) -> Coordinates of nearest food piece
    def set_input_values(self, x, y):
        # Send the distance in X and Y as inputs to the Network
        if x == self.x[0]/game.STEP:
            self.inputX = 10
        else:
            self.inputX = 1 / (x - self.x[0]/game.STEP)

        if y == self.y[0]/game.STEP:
            self.inputY = 10
        else:
            self.inputY = 1 / (y - self.y[0]/game.STEP)

        # Distances to the walls are also sent as inputs
        if self.y[0] == 0:
            self.inputDistanceTop = 10
        else:
            self.inputDistanceTop = 1 / self.y[0]/game.STEP

        if game.Game.WIDTH == self.x[0]:
            self.inputDistanceRight = 10
        else:
            self.inputDistanceRight = 1 / (game.Game.WIDTH - self.x[0])/game.STEP

        if game.Game.HEIGHT == self.y[0]:
            self.inputDistanceBottom = 10
        else:
            self.inputDistanceBottom = 1 / (game.Game.HEIGHT - self.y[0])/game.STEP

        if self.x[0] == 0:
            self.inputDistanceLeft = 10
        else:
            self.inputDistanceLeft = 1 / self.x[0]/game.STEP

        # Inputs represent what lays on the next tile, to the right and to the left
        # next_x, next_y = self.get_next_x_y()
        # if x == next_x and y == next_y:
        #     self.inputNextTile = 1
        # elif 0 < next_x <= game.Game.WIDTH or 0 < next_y <= game.Game.HEIGHT:
        #     self.inputNextTile = -1
        # elif self.collided_on_self(x1=next_x, y1=next_y):
        #     self.inputNextTile = -1
        # else:
        #     self.inputNextTile = 0
        #
        # right_x, right_y = self.turn(dir_=0)
        # left_x, left_y = self.turn(dir_=1)
        #
        # if x == right_x and y == right_y:
        #     self.inputRightTile = 1
        # elif 0 < right_x <= game.Game.WIDTH or 0 < right_y <= game.Game.HEIGHT:
        #     self.inputRightTile = -1
        # elif self.collided_on_self(x1=right_x, y1=right_y):
        #     self.inputRightTile = -1
        # else:
        #     self.inputRightTile = 0
        #
        # if x == left_x and y == left_y:
        #     self.inputLeftTile = 1
        # elif 0 < left_x <= game.Game.WIDTH or 0 < left_y <= game.Game.HEIGHT:
        #     self.inputLeftTile = -1
        # elif self.collided_on_self(x1=left_x, y1=left_y):
        #     self.inputLeftTile = -1
        # else:
        #     self.inputLeftTile = 0

    def calc_fitness(self, penalty=1):
        self.fitness = 1 / math.exp(self.foodCount - penalty - (time.time()-self.timeLastFood)/2)\
                       # + 1/math.exp(penalty)\
                       # + 1/math.exp(self.groundCovered/5)

    def reset(self, x=-1, y=-1):
        self.isDead = False
        self.x = []
        self.y = []
        self.length = self.INITIAL_LENGTH

        if x < 0 or y < 0:
            x = self.INITIAL_X
            y = self.INITIAL_Y

        for i in range(self.length):
            self.x.append(game.STEP * self.MUL * (x - i))
            self.y.append(game.STEP * self.MUL * y)

        self.updateCount = 0
        self.foodCount = 0
        self.groundCovered = 0
        self.lastMoves = [0, 0]

    def print_network(self, run):
        network = self.network

        network_data = {"network": network.k, "hidden_nodes": [],
                        "output_nodes": [], "sensor_nodes": [],
                        "generations": run}
        for neuron in network.inputOutputNodeList:
            network_data["hidden_nodes"].append({neuron.k: {"output_synapses": [],
                                                            "input_synapses": []}})

            x = network_data["hidden_nodes"][-1][neuron.k]["output_synapses"]
            for synapse in neuron.outputList:
                x.append({synapse.k: synapse.weight,
                          "other_end": synapse.destinationNeuron.k})

            x = network_data["hidden_nodes"][-1][neuron.k]["input_synapses"]
            for synapse in neuron.inputList:
                x.append({synapse.k: synapse.weight,
                          "other_end": synapse.sourceNeuron.k})

        for neuron in network.sensorList:
            network_data["sensor_nodes"].append({neuron.k: {"output_synapses": []}})

            x = network_data["sensor_nodes"][-1][neuron.k]["output_synapses"]
            for synapse in neuron.outputList:
                x.append({synapse.k: synapse.weight,
                          "other_end": synapse.destinationNeuron.k})

        for neuron in network.actuatorList:
            network_data["output_nodes"].append({neuron.k: {"input_synapses": []}})

            x = network_data["output_nodes"][-1][neuron.k]["input_synapses"]
            for synapse in neuron.inputList:
                x.append({synapse.k: synapse.weight,
                          "other_end": synapse.sourceNeuron.k})

        return network_data
