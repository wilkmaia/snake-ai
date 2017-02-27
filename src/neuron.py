import math
import random

from src.network import Network


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


visitedNeurons = []


class Neuron:
    def __init__(self):
        self.z = 0
        self.bias = random.gauss(0, 1)
        self.k = random.random()

        self._input_list = []
        self._output_list = []
        self.bias = 0
        self._output = 0

    def activate(self, m=0):
        m += 1
        # print("m =", m)

        if len(self.input_list) == 0:
            return self.output

        self.z = 0
        for syn in self.input_list:
            # print("Input List:", self.input_list)
            if syn.getSourceNeuron() in visitedNeurons:
                continue

            visitedNeurons.append(syn.getSourceNeuron())
            # print("Source Neuron:", syn.getSourceNeuron())

            self.z += syn.getWeight() * syn.getSourceNeuron().activate(m)
        # print("Visited Neurons:", visitedNeurons)

        return sigmoid(Network.EPSILON * self.z)

    @property
    def input_list(self):
        return self._input_list

    @input_list.setter
    def input_list(self, s):
        self._input_list.append(s)

    @property
    def output_list(self):
        return self._output_list

    @output_list.setter
    def output_list(self, s):
        self._output_list.append(s)

    @property
    def output(self):
        return self._output

    @output.setter
    def output(self, val):
        self._output = val

    def __key(self):
        return (self.k)

    def __hash__(self):
        return hash(self.__key())
