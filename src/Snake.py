from enum import Enum
import Game
from Network import Network
from Neuron import Neuron
import random

class Direction(Enum):
	UP = 0
	RIGHT = 1
	DOWN = 2
	LEFT = 3

class Snake:
	STEP = 42
	PROP_CCW = 0.45
	PROP_CW = 0.65

	updateCountMax = 2

	def __init__(self, length, step, snakeN=1):
		self.x = []
		self.y = []
		self.length = length
		self.INITIAL_LENGTH = length
		self.DIRECTION = Direction.RIGHT

		self.updateCount = 0
		self.STEP = step
		for i in range(length):
			xN = random.randint(0, Game.Game.MAX_COORD)
			yN = random.randint(0, Game.Game.MAX_COORD)
			self.x.append(self.STEP * (xN - i))
			self.y.append(self.STEP * yN)

		self.NETWORK = Network(mutRate=1)
		self.snakeNumber = snakeN

		self.foodCount = 0

		self.isDead = False

		self.fitness = 0
		self.input_list = []
		self.setupNetwork()

		self.snakeNumber = 1

	# dir
	# 0 -> Clockwise
	# 1 -> Counterclockwise
	def turn(self, dir = 0):
		numDir = len(list(Direction))

		if dir == 0:
			nextDirValue = (self.DIRECTION.value + 1) % numDir
		elif dir == 1:
			if self.DIRECTION.value == 0:
				nextDirValue = 3
			else:
				nextDirValue = (self.DIRECTION.value - 1)

		self.DIRECTION = Direction(nextDirValue)

	def update(self):
		self.updateCount = self.updateCount + 1
		if self.updateCount >= self.updateCountMax:
			self.NETWORK.setInputValues([self.inputX, self.inputY, self.wallDistance])
			prop = self.NETWORK.propagate()

			#print("Snake #", self.snakeNumber, "prop = ", prop)
			if prop <= self.PROP_CCW:
				self.turn(dir=1)
			elif prop >= self.PROP_CW:
				self.turn(dir=0)

			for i in range(self.length-1, 0, -1):
				self.x[i] = self.x[i-1]
				self.y[i] = self.y[i-1]

			if self.DIRECTION == Direction.UP:
				self.y[0] -= self.STEP
			elif self.DIRECTION == Direction.RIGHT:
				self.x[0] += self.STEP
			elif self.DIRECTION == Direction.DOWN:
				self.y[0] += self.STEP
			elif self.DIRECTION == Direction.LEFT:
				self.x[0] -= self.STEP

			self.updateCount = 0

	def draw(self, surface, image):
		if self.isDead == True:
			return

		for i in range(self.length):
			surface.blit(image, (self.x[i], self.y[i]))

	def collidedOnSelf(self):
		x1 = self.x[0]
		y1 = self.y[0]
		for i in range(1, self.length):
			if Game.checkCollision(self.STEP, x1, y1, self.x[i], self.y[i]) == True:
				return True

		return False

	def foundFood(self):
		i = self.length
		self.length += 1
		self.foodCount += 1

		self.x.append(self.x[i-1])
		self.y.append(self.y[i-1])

	def setSnakeNetwork(self, net):
		self.NETWORK = net

	def getSnakeNetwork(self):
		return self.NETWORK

	def setupNetwork(self):
		self.input_list.append(Neuron())
		self.input_list.append(Neuron())
		self.input_list.append(Neuron())

		self.NETWORK.setSensorList(self.input_list)
		self.NETWORK.setInputValues([Game.Game.WIDTH, Game.Game.HEIGHT, Game.Game.WIDTH - self.STEP])


	def setInputValues(self, x, y):
		# Send the distance in X and Y as inputs to the Network
		self.inputX = x - self.x[0]
		self.inputY = y - self.y[0]
		if self.DIRECTION == Direction.UP:
			self.wallDistance = self.y[0]
		elif self.DIRECTION == Direction.RIGHT:
			self.wallDistance = Game.Game.WIDTH - self.x[0]
		elif self.DIRECTION == Direction.DOWN:
			self.wallDistance = Game.Game.HEIGHT - self.y[0]
		elif self.DIRECTION == Direction.LEFT:
			self.wallDistance = self.x[0]

	def calcFitness(self, penalty=0):
		self.fitness = 3 / ( 0.5 + self.foodCount ) + 1 / penalty

	def reset(self):
		self.isDead = False;
		self.x = [];
		self.y = [];
		self.length = self.INITIAL_LENGTH;
		for i in range(self.length):
			xN = random.randint(0, Game.Game.MAX_COORD)
			yN = random.randint(0, Game.Game.MAX_COORD)
			self.x.append(self.STEP * (xN - i))
			self.y.append(self.STEP * yN)

		self.updateCount = 0;
		self.foodCount = 0;
