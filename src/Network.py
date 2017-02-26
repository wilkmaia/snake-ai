# Neural network consisting of 1 output neuron and
# 2 input neurons (sensors)
# The hidden layer(s) is(are) gonna be arranged by a GA

from Neuron import Neuron
from Neuron import visitedNeurons
from Synapse import Synapse
import random

class Network:
	MUTATION_RATE = 0.5
	INNER_MUTATION_RATE = 0.3
	EPSILON = 0.1

	def __init__(self, mutRate=1):
		self.sensor_list = []
		self.inputNode_list = []
		self.outputNode_list = []
		self.inputOutputNode_list = []

		self.actuator = Neuron()

		self.outputNode_list.append(self.actuator)
		self.MUTATION_RATE = mutRate

	def propagate(self):
		visitedNeurons.clear()
		
		prop = self.actuator.activate()
		return prop

	def setInputNodeList(self, l):
		self.inputNode_list = l

	def setOutputNodeList(self, l):
		self.outputNode_list = l

	def setInputOutputNodeList(self, l):
		self.inputOutputNode_list = l

	def setSensorList(self, l):
		self.sensor_list = l
		self.inputNode_list += l

	def setActuator(self, n):
		self.actuator = n
		self.outputNode_list.append(n)

	def setInputValues(self, l):
		if len(self.sensor_list) != len(l):
			print("########### ERROR setInputValues")

		i = 0
		for sensor in self.sensor_list:
			sensor.setOutput(l[i])
			i += 1

	def getRandomNeuron(self, l):
		idx = random.randint(0, len(l) - 1)
		return l[idx]

	def mutate(self):
		r = random.random()
		if r <= self.MUTATION_RATE:
			self.mutateChangeWeights()

			if r <= self.INNER_MUTATION_RATE:
				mut_type = random.randint(0, 3)
				if mut_type == 0:
					self.mutateAddNeuron()
				elif mut_type == 1:
					self.mutateRemoveNeuron()
				elif mut_type == 2:
					self.mutateChangeWeights()
				elif mut_type == 3:
					self.mutateAddSynapse()

	def mutateChangeWeights(self):
		if len(self.inputOutputNode_list) > 0:
			tmp = self.getRandomNeuron(self.inputOutputNode_list)
			for syn in tmp.getInputList():
				syn.setWeight(random.random())

	def mutateRemoveNeuron(self):
		if len(self.inputOutputNode_list) > 0:
			tmp = self.getRandomNeuron(self.inputOutputNode_list)
			for syn in tmp.getOutputList():
				syn.getDestinationNeuron().getInputList().remove(syn)
			for syn in tmp.getInputList():
				syn.getSourceNeuron().getOutputList().remove(syn)

			tmp.getInputList().clear()
			tmp.getOutputList().clear()

			self.outputNode_list.remove(tmp)
			self.inputNode_list.remove(tmp)
			self.inputOutputNode_list.remove(tmp)

	def mutateAddNeuron(self):
		tmp = Neuron()

		src = self.getRandomNeuron(self.inputNode_list)
		synIn = Synapse(src, tmp, self.EPSILON * random.random())
		src.addOutput(synIn)
		tmp.addInput(synIn)

		dst = self.getRandomNeuron(self.outputNode_list)
		synOut = Synapse(tmp, dst, self.EPSILON * random.random())
		tmp.addOutput(synOut)
		dst.addInput(synOut)

		self.inputNode_list.append(tmp)
		self.outputNode_list.append(tmp)
		self.inputOutputNode_list.append(tmp)

	def mutateAddSynapse(self):
		src = self.getRandomNeuron(self.inputNode_list)
		dst = src
		while src == dst:
			dst = self.getRandomNeuron(self.outputNode_list)

		syn = Synapse(src, dst, self.EPSILON * random.random())
		src.addOutput(syn)
		dst.addInput(syn)

	def copy(self):
		q = []
		m = {}
		copyNetwork = Network()

		originalActuator = self.actuator

		copyActuator = Neuron()
		copyNetwork.setActuator(copyActuator)

		q.append(originalActuator)
		m[originalActuator] = copyActuator
		copyActuator.k = originalActuator.k

		copyioNodes = []
		copyiNodes = []
		copyoNodes = []
		copySensors = []

		for sensor in self.sensor_list:
			tmp = Neuron()
			m[sensor] = tmp
			q.append(sensor)
			copySensors.append(tmp)
			copyiNodes.append(tmp)

		while len(q) > 0:
			originalNode = q.pop()

			iSyns = originalNode.getInputList()
			oSyns = originalNode.getOutputList()

			copyNode = m[originalNode]
			copyNode.k = originalNode.k

			for syn in iSyns:
				inputOriginal = syn.getSourceNeuron()

				if inputOriginal in list(m.keys()):
					inputCopy = m[inputOriginal]

					exists = False
					for n in inputCopy.getOutputList():
						if n.getSourceNeuron() == inputCopy and n.getDestinationNeuron() == copyNode:
							exists = True
							break
					if exists == False:
						copySyn = Synapse(inputCopy, copyNode, syn.getWeight())
						copyNode.addInput(copySyn)
						inputCopy.addOutput(copySyn)
				else:
					inputCopy = Neuron()
					inputCopy.k = inputOriginal.k
					copyioNodes.append(inputCopy)

					copySyn = Synapse(inputCopy, copyNode, syn.getWeight())
					inputCopy.addOutput(copySyn)
					copyNode.addInput(copySyn)
					m[inputOriginal] = inputCopy
					q.append(inputOriginal)

			for syn in oSyns:
				outputOriginal = syn.getDestinationNeuron()

				if outputOriginal in list(m.keys()):
					outputCopy = m[outputOriginal]

					exists = False
					for n in outputCopy.getOutputList():
						if n.getSourceNeuron() == copyNode and n.getDestinationNeuron() == outputCopy:
							exists = True
							break
					if exists == False:
						copySyn = Synapse(copyNode, outputCopy, syn.getWeight())
						copyNode.addOutput(copySyn)
						outputCopy.addInput(copySyn)
				else:
					outputCopy = Neuron()
					outputCopy.k = outputOriginal.k
					copyioNodes.append(outputCopy)

					copySyn = Synapse(copyNode, outputCopy, syn.getWeight())
					outputCopy.addInput(copySyn)
					copyNode.addOutput(copySyn)
					m[outputOriginal] = outputCopy
					q.append(outputOriginal)

		for n in copyioNodes:
			copyiNodes.append(n)
			copyoNodes.append(n)
		copyoNodes.append(copyActuator)

		copyNetwork.setSensorList(copySensors)
		copyNetwork.setInputNodeList(copyiNodes)
		copyNetwork.setOutputNodeList(copyoNodes)
		copyNetwork.setInputOutputNodeList(copyioNodes)

		return copyNetwork
