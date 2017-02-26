import random
import math
import Network

def sigmoid(x):
	return 1 / (1 + math.exp(-x))

visitedNeurons = []

class Neuron:
	def __init__(self):
		self.z = 0
		self.bias = random.gauss(0, 1)
		self.k = random.random()

		self.input_list = []
		self.output_list = []
		self.bias = 0
		self.y = 0

	def activate(self, m=0):
		m +=1
		#print("m =", m)

		if len(self.input_list) == 0:
			return self.y

		self.z = 0
		for syn in self.input_list:
			#print("Input List:", self.input_list)
			if syn.getSourceNeuron() in visitedNeurons:
				continue

			visitedNeurons.append(syn.getSourceNeuron())
			#print("Source Neuron:", syn.getSourceNeuron())

			self.z += syn.getWeight() * syn.getSourceNeuron().activate(m)
			#print("Visited Neurons:", visitedNeurons)

		return sigmoid(Network.Network.EPSILON * self.z)

	def addInput(self, s):
		self.input_list.append(s)

	def addOutput(self, s):
		self.output_list.append(s)

	def getInputList(self):
		return self.input_list

	def getOutputList(self):
		return self.output_list

	def getOutput(self):
		return self.y

	def setOutput(self, val):
		self.y = val

	def __key(self):
		return (self.k)

	def __hash__(self):
		return hash(self.__key())
