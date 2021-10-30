import copy


class Territory():
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

    def setArmy(self, value):
        if(value < 1):
            raise Exception("Error: Army value cannot be less than 1")
        else:
            self.army = value

    def addArmy(self, value):
        self.army += value
        if(self.army < 1):
            raise Exception("Error: Army value cannot be less than 1")

    def __deepcopy__(self):
        cpy = Territory
        cpy.index = self.index
        cpy.connections = copy.deepcopy(self.connections)
        cpy.continent = self.continent
        cpy.position = self.position
        cpy.owner = self.owner
        cpy.army = self.army
        return cpy
