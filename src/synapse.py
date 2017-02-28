import random


class Synapse:
    def __init__(self, source_neuron, destination_neuron, weight):
        self.sourceNeuron = source_neuron
        self.destinationNeuron = destination_neuron
        self.weight = weight
        self.k = random.randint(0, 99999999)

    def __key(self):
        return self.k

    def __eq__(self, other):
        return self.k == other.k

    def __hash__(self):
        return hash(self.__key())