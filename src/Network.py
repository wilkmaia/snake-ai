# Neural network consisting of 4 output neurons and
# 10 input neurons (sensors)
# The hidden layer(s) is(are) gonna be arranged by a GA

import random

from neuron import Neuron
from neuron import visitedNeurons
from synapse import Synapse


def get_random_element(list_):
    idx = random.randint(0, len(list_) - 1)
    return list_[idx]


class Network:
    MUTATION_RATE = 0.7
    INNER_MUTATION_RATE = 0.3

    def __init__(self, mut_rate=1):
        self.sensorList = []
        self.inputNodeList = []
        self.outputNodeList = []
        self.inputOutputNodeList = []

        self.actuatorList = []
        self.actuatorList.append(Neuron())
        self.actuatorList.append(Neuron())
        self.actuatorList.append(Neuron())
        self.actuatorList.append(Neuron())

        self.outputNodeList.extend(self.actuatorList)
        self.MUTATION_RATE = mut_rate
        self.EPSILON = random.randint(-1000, 1000) / 1000

    def activate(self):
        p = []
        for neuron in self.actuatorList:
            p.append(neuron.activate())
        return p

    def propagate(self):
        visitedNeurons.clear()
        return self.activate()

    def set_input_values(self, list_):
        if len(self.sensorList) != len(list_):
            # print("########### ERROR set_input_values - {} {}".format(len(self.sensorList), len(list_)))
            # print("sensorList =", self.sensorList)
            # print("list_ =", list_)
            print(len(self.sensorList))
            # return

        i = 0
        for sensor in self.sensorList:
            sensor.y = list_[i]
            i += 1

    def mutate(self):
        r = random.random()
        if r <= self.MUTATION_RATE:
            self.mutate_change_weights()

            if r <= self.INNER_MUTATION_RATE:
                mut_type = random.randint(0, 3)
                mutation_list = ["Add Neuron",
                                 "Remove Neuron",
                                 "Change Weights",
                                 "Add Synapse"]
                print("Mutating:", mutation_list[mut_type])
                if mut_type == 0:
                    self.mutate_add_neuron()
                elif mut_type == 1:
                    self.mutate_remove_neuron()
                elif mut_type == 2:
                    self.mutate_change_weights()
                elif mut_type == 3:
                    self.mutate_add_synapse()

    def mutate_change_weights(self):
        if len(self.inputOutputNodeList) > 0:
            tmp = get_random_element(self.inputOutputNodeList)
            for syn in tmp.inputList:
                syn.weight = random.uniform(-1, 1)

    def mutate_remove_neuron(self):
        if len(self.inputOutputNodeList) > 0:
            tmp = get_random_element(self.inputOutputNodeList)
            for syn in tmp.outputList:
                syn.destinationNeuron.inputList.remove(syn)
            for syn in tmp.inputList:
                syn.sourceNeuron.outputList.remove(syn)

            tmp.inputList.clear()
            tmp.outputList.clear()

            self.outputNodeList.remove(tmp)
            self.inputNodeList.remove(tmp)
            self.inputOutputNodeList.remove(tmp)

    def mutate_add_neuron(self):
        tmp = Neuron()

        src = get_random_element(self.inputNodeList)
        syn_in = Synapse(src, tmp, random.uniform(-1, 1))
        src.add_output(syn_in)
        tmp.add_input(syn_in)

        dst = get_random_element(self.outputNodeList)
        syn_out = Synapse(tmp, dst, random.uniform(-1, 1))
        tmp.add_output(syn_out)
        dst.add_input(syn_out)

        self.inputNodeList.append(tmp)
        self.outputNodeList.append(tmp)
        self.inputOutputNodeList.append(tmp)

    def mutate_add_synapse(self):
        src = get_random_element(self.inputNodeList)
        dst = src
        while src == dst:
            dst = get_random_element(self.outputNodeList)

        syn = Synapse(src, dst, random.uniform(-1, 1))
        src.add_output(syn)
        dst.add_input(syn)

    def copy(self):
        q = []
        m = {}
        copy_network = Network()

        original_actuator_list = self.actuatorList

        copy_actuator_list = [Neuron(), Neuron(), Neuron(), Neuron()]
        copy_network.actuatorList = copy_actuator_list

        for i in range(len(original_actuator_list)):
            q.append(original_actuator_list[i])
            m[original_actuator_list[i]] = copy_actuator_list[i]
            copy_actuator_list[i].k = original_actuator_list[i].k

        copy_io_nodes = []
        copy_i_nodes = []
        copy_o_nodes = []
        copy_sensors = []

        for sensor in self.sensorList:
            tmp = Neuron()
            m[sensor] = tmp
            tmp.k = sensor.k
            q.append(sensor)

            copy_sensors.append(tmp)
            copy_i_nodes.append(tmp)

        while len(q) > 0:
            original_node = q.pop()

            i_syns = original_node.inputList
            o_syns = original_node.outputList

            copy_node = m[original_node]
            copy_node.k = original_node.k

            for syn in i_syns:
                input_original = syn.sourceNeuron

                if input_original in list(m.keys()):
                    input_copy = m[input_original]

                    exists = False
                    for n in input_copy.outputList:
                        if n.sourceNeuron == input_copy and n.destinationNeuron == copy_node:
                            exists = True
                            break
                    if not exists:
                        copy_syn = Synapse(input_copy, copy_node, syn.weight)
                        copy_node.add_input(copy_syn)
                        input_copy.add_output(copy_syn)
                else:
                    input_copy = Neuron()
                    input_copy.k = input_original.k
                    copy_io_nodes.append(input_copy)

                    copy_syn = Synapse(input_copy, copy_node, syn.weight)
                    input_copy.add_output(copy_syn)
                    copy_node.add_input(copy_syn)
                    m[input_original] = input_copy
                    q.append(input_original)

            for syn in o_syns:
                output_original = syn.destinationNeuron

                if output_original in list(m.keys()):
                    output_copy = m[output_original]

                    exists = False
                    for n in output_copy.inputList:
                        if n.sourceNeuron == copy_node and n.destinationNeuron == output_copy:
                            exists = True
                            break
                    if not exists:
                        copy_syn = Synapse(copy_node, output_copy, syn.weight)
                        copy_node.add_output(copy_syn)
                        output_copy.add_input(copy_syn)
                else:
                    output_copy = Neuron()
                    output_copy.k = output_original.k
                    copy_io_nodes.append(output_copy)

                    copy_syn = Synapse(copy_node, output_copy, syn.weight)
                    output_copy.add_input(copy_syn)
                    copy_node.add_output(copy_syn)
                    m[output_original] = output_copy
                    q.append(output_original)

        for n in copy_io_nodes:
            copy_i_nodes.append(n)
            copy_o_nodes.append(n)
        copy_o_nodes.extend(copy_actuator_list)

        copy_network.sensorList = copy_sensors
        copy_network.inputNodeList = copy_i_nodes
        copy_network.outputNodeList = copy_o_nodes
        copy_network.inputOutputNodeList = copy_io_nodes

        return copy_network
