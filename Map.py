import sys
from Territory import Territory
import math
import copy


class Map():
    def __init__(self):
        super().__init__()
        self.territories = {}
        # TODO: Make these readable from the MapData instead of hardcoded
        self.continentColors = {
            "North America": (255, 255, 0),  # Yellow
            "South America": (255, 0, 0),  # Red
            "Europe": (200, 200, 200),  # Grey
            "Africa": (0, 255, 0),  # Green
            "Asia": (0, 0, 255),  # Blue
            "Australia": (255, 0, 255)  # Pink
        }

        self.continentCount = {}

    def __deepcopy__(self):
        cpy = Map()

        for k in self.territories.keys():
            cpy.territories[k] = copy.deepcopy(cpy.territories[k])

        cpy.continentColors = copy.deepcopy(self.continentColors)

        cpy.continentCount = copy.deepcopy(self.continentCount)

    def getPositions(self):
        positions = {}
        for territory in self.territories:
            positions[territory.index] = territory.position
        return positions

    def getTotalArmiesByPlayer(self, playerName):
        return sum([x.army for x in self.getTerritoriesByPlayer(playerName)])

    def getTerritoriesByPlayer(self, playerName):
        return [x for x in self.territories.values() if x.owner == playerName]

    def getPlayerTerritories(self):
        players = {}
        for territoryIndex, territoryData in self.territories.items():
            if(territoryData.owner not in players):
                players[territoryData.owner] = []
            players[territoryData.owner].append(territoryIndex)
        return players

    def placeArmy(self, playerName, amount, territoryId):
        if(territoryId < 0 or territoryId > len(self.territories)):
            raise Exception(f"The territory id {territoryId} is not a valid id.")
        territory = self.territories[territoryId]
        if(territory.owner and territory.owner != playerName):
            raise Exception(f"Player '{playerName}' is \
                        trying to place {amount} armies \
                        at {territoryId} controlled by \
                        {self.owners[territoryId]}")
        else:
            territory.army += amount
            territory.owner = playerName

    def getContinentBonus(self, playerName):
        unitCount = 0

        # TODO: Find a way to make these read from a file instead of hardcoded
        naCount = len([x for x in self.getTerritoriesByContinent("North America") if x.owner == playerName])
        saCount = len([x for x in self.getTerritoriesByContinent("South America") if x.owner == playerName])
        euCount = len([x for x in self.getTerritoriesByContinent("Europe") if x.owner == playerName])
        afCount = len([x for x in self.getTerritoriesByContinent("Africa") if x.owner == playerName])
        asCount = len([x for x in self.getTerritoriesByContinent("Asia") if x.owner == playerName])
        auCount = len([x for x in self.getTerritoriesByContinent("Australia") if x.owner == playerName])

        unitCount += 5 if naCount == self.continentCount["North America"] else 0
        unitCount += 2 if saCount == self.continentCount["South America"] else 0
        unitCount += 5 if euCount == self.continentCount["Europe"] else 0
        unitCount += 3 if afCount == self.continentCount["Africa"] else 0
        unitCount += 7 if asCount == self.continentCount["Asia"] else 0
        unitCount += 2 if auCount == self.continentCount["Australia"] else 0

        return unitCount

    def getNewUnitCountForPlayer(self, playerName):
        # Get "normal" unit amount based on territory count
        territoryCount = len(self.getTerritoriesByPlayer(playerName))
        unitCount = math.floor(territoryCount / 3)
        # You always get at least 3 units
        unitCount = max(unitCount, 3)

        # Continent bonuses
        unitCount += self.getContinentBonus(playerName)

        return unitCount

    def getTerritoriesByContinent(self, continentName):
        return [x for x in self.territories.values() if x.continent == continentName]

    def updateContinentCount(self):
        continentCounts = {}
        for continentName in self.continentColors.keys():
            continentCounts[continentName] = len(self.getTerritoriesByContinent(continentName))
        self.continentCount = continentCounts

    def moveArmies(self, supplyIndex, receiveIndex, amount):
        self.territories[supplyIndex].army -= amount
        self.territories[receiveIndex].army += amount
