import random
from Agent import Agent
import math
import copy


class Population:
    def __init__(self, popSize):
        self.allAgents = []
        self.popSize = popSize
        self.nameSymbols = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&+-|?<>."

        self.initAllAgents()

    def clear(self):
        self.allAgents = []

    def getNameSymbols(self, size=2):
        return (''.join(random.choice(self.nameSymbols) for _ in range(size)))

    def initAllAgents(self, initialMutations=10.0, mutationMultiplier=2.0):
        self.allAgents = []
        for i in range(self.popSize):
            name = self.getNameSymbols()
            agent = Agent(name)
            for _ in range(initialMutations):
                for characteristicGroupName in agent.characteristics.keys():
                    agent.mutateCharacteristic(characteristicGroupName, True, mutationMultiplier)
            self.allAgents.append(agent)

    def generateNextGeneration(self, mutationMultiplier=1.0):
        maxSelectionIndex = len(self.allAgents)
        while(len(self.allAgents) < self.popSize):
            baseAgentIndex = math.floor(maxSelectionIndex * random.random())
            baseAgent = self.allAgents[baseAgentIndex]
            newAgent = copy.deepcopy(baseAgent)
            newAgent.name = newAgent.name + self.getNameSymbols()
            newAgent.mutate(mutationMultiplier=mutationMultiplier)
            self.allAgents.append(newAgent)

    def getMatchGroups(self, groupSize=2):
        matchUps = []
        for i in range(0, len(self.entries), groupSize):
            matchUp = self.entries[i: i+groupSize]
            matchUps.append(matchUp)
        return matchUps
