import sys
from Territory import Territory
from Continent import Continent
import math
import copy


class Map():
    def __init__(self):
        super().__init__()
        self.territories = {}
        # TODO: Make these readable from the MapData instead of hardcoded
        self.continents = {}

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

        for continent in self.continents.values():
            unitCount += continent.unitBonus if all(x.owner == playerName for x in self.getTerritoriesByContinent(continent.name)) else 0
        
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

    def moveArmies(self, supplyIndex, receiveIndex, amount):
        self.territories[supplyIndex].army -= amount
        self.territories[receiveIndex].army += amount
