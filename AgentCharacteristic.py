import math
import random


class AgentCharacteristic:
    def __init__(self,
                 value,
                 description,
                 adjustmentAmt=1.0,
                 lowerLimit=-math.inf,
                 upperLimit=math.inf):
        self.value = value
        self.description = description
        self.adjustmentAmt = adjustmentAmt
        self.lowerLimit = lowerLimit
        self.upperLimit = upperLimit

    def __int__(self):
        return self.value

    def __deepcopy__(self):
        cpy = AgentCharacteristic()
        cpy.value = self.value
        cpy.description = self.description
        cpy.adjustmentAmt = self.adjustmentAmt
        return cpy

    def toJSON(self):
        return f"{{\"value\" : {self.value}, \"adjustmentAmount\" : {self.adjustmentAmt}, \"lowerLimit\" : {self.lowerLimit}, \"upperLimit\" : {self.upperLimit}, \"description\" : \"{self.description}\"}}"

    def adjust(self):
        self.adjust(self.adjustmentAmt)

    def adjust(self, amt):
        self.value += amt
        if (self.value > self.upperLimit):
            self.value = self.upperLimit
        elif (self.value < self.lowerLimit):
            self.value = self.lowerLimit

    def adjust_negative(self):
        self.adjust(-self.adjustmentAmt)

    def adjust_negative(self, amt):
        self.adjust(-amt)

    def adjust_random(self):
        if (bool(random.getrandbits(1))):
            self.adjust()
        else:
            self.adjust_negative()

    def adjust_random(self, amt):
        if (bool(random.getrandbits(1))):
            self.adjust(amt)
        else:
            self.adjust_negative(amt)

