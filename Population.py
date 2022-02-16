import random
from RiskAgent import RiskAgent
import math
import copy


class Population:
    def __init__(self, popSize):
        self.allAgents = []
        self.popSize = popSize
        self.nameSymbols = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"

        self.initAllAgents()

    def __len__(self):
        return len(self.allAgents)

    def clear(self):
        self.allAgents = []

    def getNameSymbols(self, size=16):
        return (''.join(random.choice(self.nameSymbols) for _ in range(size)))

    def initAllAgents(self, initialMutations=10, mutationMultiplier=2.0):
        self.allAgents = []
        for i in range(self.popSize):
            name = self.getNameSymbols()
            name = name + "+" + name
            agent = RiskAgent(name)
            for _ in range(initialMutations):
                for characteristicGroupName in agent.characteristics.keys():
                    agent.mutateCharacteristic(characteristicGroupName, True, mutationMultiplier)
            self.allAgents.append(agent)

    def generateNextGeneration(self, mutationMultiplier=1.0):
        maxSelectionIndex = len(self.allAgents)
        while(len(self.allAgents) < self.popSize):
            baseAgentIndex = math.floor(maxSelectionIndex * random.random())
            baseAgent = self.allAgents[baseAgentIndex]
            newAgent = baseAgent.clone()
            newAgent.name = baseAgent.name.split("+")[1] + "+" + self.getNameSymbols()
            newAgent.mutate(mutationMultiplier=mutationMultiplier)
            self.allAgents.append(newAgent)

    def getMatchGroups(self, groupSize=2):
        matchUps = []
        for i in range(0, len(self.allAgents), groupSize):
            matchUp = self.allAgents[i: i+groupSize]
            matchUps.append(matchUp)
        return matchUps

    def addAgent(self, agent):
        self.allAgents.append(agent)

    def addAgents(self, agentList):
        for agent in agentList:
            self.allAgents.append(agent)

    def getAverageAgent(self, name="Average Agent"):
        # Creates a new agent with characteristics set to the average characteristic value of the population
        avgAgent = RiskAgent(name)
        # Reset avgAgent's values back to zero
        for categoryName, characteristicCategory in avgAgent.characteristics.items():
            for characteristicName, characteristic in avgAgent.characteristics[categoryName].items():
                avgAgent.characteristics[categoryName][characteristicName].value = 0

        # Add each agent's values * weight to avgAgent
        #   The weight removes the need to divide by the
        #   total number after the summation like you
        #   would do when typically calculating the average
        valueWeight = 1/len(self.allAgents)
        for agent in self.allAgents:
            for categoryName, characteristicCategory in agent.characteristics.items():
                for characteristicName, characteristic in agent.characteristics[categoryName].items():
                    avgAgent.characteristics[categoryName][characteristicName].value += agent.characteristics[categoryName][characteristicName].value * valueWeight

        return avgAgent
