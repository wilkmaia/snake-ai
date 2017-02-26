class Synapse:
	def __init__(self, sourceNeuron, destinationNeuron, weight):
		self.sourceNeuron = sourceNeuron
		self.destinationNeuron = destinationNeuron
		self.weight = weight

	def getSourceNeuron(self):
		return self.sourceNeuron

	def getDestinationNeuron(self):
		return self.destinationNeuron

	def getWeight(self):
		return self.weight

	def setWeight(self, w):
		self.weight = w

	def setSourceNeuron(self, s):
		self.sourceNeuron = s

	def setDestinationNeuron(self, d):
		self.destinationNeuron = d