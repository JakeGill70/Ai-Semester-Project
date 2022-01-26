class Continent():
    def __init__(self, name, unitBonus, color):
        self.name = name
        self.unitBonus = unitBonus
        self.color = color

    def getJson(self):
        return f'{{"name":"{self.name}", "unitBonus":{self.unitBonus}, "color":{self.color}}}'