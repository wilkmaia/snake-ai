import random
import math

import network


def sigmoid(x):
    return 1 / (1 + math.exp(-x))

visitedNeurons = []


class Neuron:
    def __init__(self):
        self.z = 0
        self.y = 0
        self.k = random.random()

        self.inputList = []
        self.outputList = []

    def activate(self):
        if len(self.inputList) == 0:
            return self.y

        self.z = 0
        for syn in self.inputList:
            if syn.sourceNeuron in visitedNeurons:
                continue

            visitedNeurons.append(syn.sourceNeuron)
            self.z += syn.weight * syn.sourceNeuron.activate()

        return sigmoid(self.z)

    def add_input(self, s):
        self.inputList.append(s)

    def add_output(self, s):
        self.outputList.append(s)

    def __key(self):
        return self.k

    def __eq__(self, other):
        return self.k == other.k

    def __hash__(self):
        return hash(self.__key())
