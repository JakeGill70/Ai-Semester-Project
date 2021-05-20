import copy


class Territory():
    def __init__(self, index, connections, continent, position):
        self.index = index
        self.connections = connections
        self.continent = continent
        self.position = position
        self.owner = ""
        self.army = 0

    def __str__(self):
        return f"#{self.index}:{self.owner}:{self.army}"

    def __deepcopy__(self):
        cpy = Territory
        cpy.index = self.index
        cpy.connections = copy.deepcopy(self.connections)
        cpy.continent = self.continent
        cpy.position = self.position
        cpy.owner = self.owner
        cpy.army = self.army
        return cpy
