# Neural network consisting of 1 output neuron and
# 2 input neurons (sensors)
# The hidden layer(s) is(are) gonna be arranged by a GA

import random

from src.neuron import Neuron, visitedNeurons
from src.synapse import Synapse


class Network:
    MUTATION_RATE = 0.5
    INNER_MUTATION_RATE = 0.3
    EPSILON = 0.1

    def __init__(self, mut_rate=1):
        self._sensor_list = []
        self.input_node_list = []
        self.output_node_list = []
        self.input_output_node_list = []

        self._actuator = Neuron()

        self.output_node_list.append(self._actuator)
        self.MUTATION_RATE = mut_rate

    def propagate(self):
        visitedNeurons.clear()

        prop = self._actuator.activate()
        return prop

    @property
    def sensor_list(self):
        return self._sensor_list

    @sensor_list.setter
    def sensor_list(self, l):
        self._sensor_list = l
        self.input_node_list += l

    @property
    def actuator(self):
        return self._actuator

    @actuator.setter
    def actuator(self, n):
        self._actuator = n
        self.output_node_list.append(n)

    def set_input_values(self, l):
        if len(self.sensor_list) != len(l):
            print("########### ERROR setInputValues")

        i = 0
        for sensor in self.sensor_list:
            sensor.setOutput(l[i])
            i += 1

    @staticmethod
    def get_random_neuron(l):
        return random.choice(l)

    def mutate(self):
        r = random.random()
        if r <= self.MUTATION_RATE:
            self.mutate_change_weights()

            if r <= self.INNER_MUTATION_RATE:
                mut_type = random.randint(0, 3)
                if mut_type == 0:
                    self.mutate_add_neuron()
                elif mut_type == 1:
                    self.mutate_remove_neuron()
                elif mut_type == 2:
                    self.mutate_change_weights()
                elif mut_type == 3:
                    self.mutate_add_synapse()

    def mutate_change_weights(self):
        if len(self.input_output_node_list) > 0:
            tmp = self.get_random_neuron(self.input_output_node_list)
            for syn in tmp.getInputList():
                syn.setWeight(random.random())

    def mutate_remove_neuron(self):
        if len(self.input_output_node_list) > 0:
            tmp = self.get_random_neuron(self.input_output_node_list)
            for syn in tmp.getOutputList():
                syn.getDestinationNeuron().getInputList().remove(syn)
            for syn in tmp.getInputList():
                syn.getSourceNeuron().getOutputList().remove(syn)

            tmp.getInputList().clear()
            tmp.getOutputList().clear()

            self.output_node_list.remove(tmp)
            self.input_node_list.remove(tmp)
            self.input_output_node_list.remove(tmp)

    def mutate_add_neuron(self):
        tmp = Neuron()

        src = self.get_random_neuron(self.input_node_list)
        syn_in = Synapse(src, tmp, self.EPSILON * random.random())
        src.addOutput(syn_in)
        tmp.addInput(syn_in)

        dst = self.get_random_neuron(self.output_node_list)
        syn_out = Synapse(tmp, dst, self.EPSILON * random.random())
        tmp.addOutput(syn_out)
        dst.addInput(syn_out)

        self.input_node_list.append(tmp)
        self.output_node_list.append(tmp)
        self.input_output_node_list.append(tmp)

    def mutate_add_synapse(self):
        src = self.get_random_neuron(self.input_node_list)
        dst = src
        while src == dst:
            dst = self.get_random_neuron(self.output_node_list)

        syn = Synapse(src, dst, self.EPSILON * random.random())
        src.addOutput(syn)
        dst.addInput(syn)

    def copy(self):
        q = []
        m = {}
        copy_network = Network()

        original_actuator = self.actuator

        copy_actuator = Neuron()
        copy_network.actuator = copy_actuator

        q.append(original_actuator)

        m[original_actuator] = copy_actuator
        copy_actuator.k = original_actuator.k

        copyio_nodes = []
        copyi_nodes = []
        copyo_nodes = []
        copy_sensors = []

        for sensor in self.sensor_list:
            tmp = Neuron()
            m[sensor] = tmp
            q.append(sensor)
            copy_sensors.append(tmp)
            copyi_nodes.append(tmp)

        while len(q) > 0:
            original_node = q.pop()

            i_syns = original_node.getInputList()
            o_syns = original_node.getOutputList()

            copy_node = m[original_node]
            copy_node.k = original_node.k

            for syn in i_syns:
                input_original = syn.getSourceNeuron()

                if input_original in list(m.keys()):
                    input_copy = m[input_original]

                    exists = False
                    for n in input_copy.getOutputList():
                        if n.getSourceNeuron() == input_copy and n.getDestinationNeuron() == copy_node:
                            exists = True
                            break
                    if not exists:
                        copy_syn = Synapse(input_copy, copy_node, syn.getWeight())
                        copy_node.addInput(copy_syn)
                        input_copy.addOutput(copy_syn)
                else:
                    input_copy = Neuron()
                    input_copy.k = input_original.k
                    copyio_nodes.append(input_copy)

                    copy_syn = Synapse(input_copy, copy_node, syn.getWeight())
                    input_copy.addOutput(copy_syn)
                    copy_node.addInput(copy_syn)
                    m[input_original] = input_copy
                    q.append(input_original)

            for syn in o_syns:
                output_original = syn.getDestinationNeuron()

                if output_original in list(m.keys()):
                    output_copy = m[output_original]

                    exists = False
                    for n in output_copy.getOutputList():
                        if n.getSourceNeuron() == copy_node and n.getDestinationNeuron() == output_copy:
                            exists = True
                            break
                    if not exists:
                        copy_syn = Synapse(copy_node, output_copy, syn.getWeight())
                        copy_node.addOutput(copy_syn)
                        output_copy.addInput(copy_syn)
                else:
                    output_copy = Neuron()
                    output_copy.k = output_original.k
                    copyio_nodes.append(output_copy)

                    copy_syn = Synapse(copy_node, output_copy, syn.getWeight())
                    output_copy.addInput(copy_syn)
                    copy_node.addOutput(copy_syn)
                    m[output_original] = output_copy
                    q.append(output_original)

        for n in copyio_nodes:
            copyi_nodes.append(n)
            copyo_nodes.append(n)
        copyo_nodes.append(copy_actuator)

        copy_network.sensor_list = copy_sensors
        copy_network.input_node_list = copyi_nodes
        copy_network.output_node_list = copyo_nodes
        copy_network.input_output_node_list = copyio_nodes

        return copy_network
