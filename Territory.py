import copy

from IJsonable import IJsonable


class Territory(IJsonable):
    def __init__(self, index, connections, continent, position, owner="", army=0):
        self.index = index
        self.connections = connections
        self.continent = continent
        self.position = position
        self.owner = owner
        self.army = army

    def __str__(self):
        return f"#{self.index}:{self.owner}:{self.army}"

    def getJson(self):
        return f'{{"index": {self.index},"connections": {self.connections},"continent": "{self.continent}","position": {self.position},"owner": "{self.owner}","army": {self.army} }}'

    def getCopy(self):
        return Territory(self.index, self.connections, self.continent, self.position, self.owner, self.army)

    def getArmy(self):
        return self.army

    def getOwner(self):
        return self.owner

    def setOwner(self, owner):
        self.owner = owner

    def setArmy(self, value):
        if(value < 1):
            raise Exception("Error: Army value cannot be less than 1")
        else:
            self.army = value

    def addArmy(self, value):
        self.army += value
        if(self.army < 1):
            raise Exception("Error: Army value cannot be less than 1")
