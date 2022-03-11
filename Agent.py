from abc import ABC, abstractmethod, ABCMeta
from argparse import ArgumentError
import hashlib
import random

from IHashable import IHashable

class Agent(IHashable, metaclass=ABCMeta):
    def __init__(self, name="Unnamed Agent"):
        self.name = name
        self.characteristics = {}

    def getJSON(self):
        s = f"{{\"name\": \"{self.name}\", \"characteristics\": {{ "
        for groupKey, groupDict in self.characteristics.items():
            s += f"\"{groupKey}\" : {{"
            for characteristicName, characteristicObject in groupDict.items():
                s += (
                    f"\"{characteristicName}\" : {characteristicObject.getJSON()},"
                )
            s = s[:-1]
            s += "},"
        s = s[:-1]
        s += "} }"
        return s

    def clone(self, cpyType=None):
        if(cpyType is None):
            cpyType = type(self)
        if(not issubclass(cpyType, Agent)):
            raise ArgumentError(cpyType, "Copy type must be of type Agent to use clone function.")

        cpy = cpyType(self.name)

        for k in self.characteristics.keys():
            for kk in self.characteristics[k].keys():
                cpy.characteristics[k][kk].value = self.characteristics[k][kk].value

        return cpy

    def mutate(self, recursiveChance=0.8, majorMutationChance=0.6, mutationMultiplier=1.0):

        recurse = True
        while (recurse):
            # Determine if recursion is necessary
            recurse = random.random() < recursiveChance
            recursiveChance = recursiveChance / 2

            # Determine what to mutate
            characteristicGroupName = random.choice(list(self.characteristics.keys()))
            # Determine how to mutate (Single attribute vs. entire group)
            isMajorMutation = random.random() < majorMutationChance
            # Perform mutation
            self.mutateCharacteristic(characteristicGroupName, isMajorMutation, mutationMultiplier)

    def mutateCharacteristic(self, characteristicGroupName, isMajorMutation=False, mutationMultiplier=1.0):
        if (isMajorMutation):
            for characteristic in self.characteristics[characteristicGroupName].values():
                characteristic.adjust_random(characteristic.adjustmentAmt * mutationMultiplier)
        else:
            randomCharacteristic = random.choice(list(self.characteristics[characteristicGroupName].values()))
            randomCharacteristic.adjust_random(randomCharacteristic.adjustmentAmt * mutationMultiplier)

    @abstractmethod
    def scoreGameState(self, gameState):
        pass