import sys
from IHashable import IHashable
from Territory import Territory
from Continent import Continent
import math
import copy
import hashlib


class Map(IHashable):
    def __init__(self):
        super().__init__()
        self.territories = {}
        self.continents = {}
        self.territoryContinentCache = None

    def __deepcopy__(self):
        cpy = Map()

        for k in self.territories.keys():
            cpy.territories[k] = copy.deepcopy(cpy.territories[k])

    def getJson(self):
        return f'{{"continents": {[c.getJson() for c in self.continents.values()]},"territories":{[t.getJson() for t in self.territories.values()]}}}'

    def getCopy(self):
        cpy = Map()

        for tk in self.territories.keys():
            cpy.territories[tk] = self.territories[tk].getCopy()

        cpy.continents = self.continents
        cpy.territoryContinentCache = self.territoryContinentCache

        return cpy

    def getTerritoryCount(self):
        return len(self.territories)

    def getPositions(self):
        positions = {}
        for territory in self.territories:
            positions[territory.index] = territory.position
        return positions

    def getTotalArmiesByPlayer(self, playerName):
        return sum([x.getArmy() for x in self.getTerritoriesByPlayer(playerName)])

    def getTerritoriesByPlayer(self, playerName):
        return [x for x in self.territories.values() if x.owner == playerName]

    def getPlayerSize(self, playerName):
        territorySize = len(self.getTerritoriesByPlayer(playerName))
        armySize = self.getTotalArmiesByPlayer(playerName)
        territoryWeight = 1000
        playerSize = territorySize * territoryWeight + armySize
        return playerSize

    def getPlayerTerritories(self):
        players = {}
        for territoryIndex, territoryData in self.territories.items():
            if (territoryData.owner not in players):
                players[territoryData.owner] = []
            players[territoryData.owner].append(territoryIndex)
        return players

    def getPlayerCount(self):
        return len(
            set([
                territoryData.owner
                for territoryData in self.territories.values()
            ]))

    def placeArmy(self, playerName, amount, territoryId):
        if (territoryId < 0 or territoryId > len(self.territories)):
            raise Exception(
                f"The territory id {territoryId} is not a valid id.")
        territory = self.territories[territoryId]
        if (territory.owner and territory.owner != playerName):
            raise Exception(f"Player '{playerName}' is \
                        trying to place {amount} armies \
                        at {territoryId} controlled by \
                        {territory.owner}")
        else:
            territory.addArmy(amount)
            territory.owner = playerName

    def getCountOfContinentsControlledByPlayer(self, playerName):
        continentCount = 0
        for continent in self.continents.values():
            continentCount += 1 if self.isContinentControlledByPlayer(continent.name, playerName) else 0
        return continentCount

    def isContinentControlledByPlayer(self, continentName, playerName):
        return all(x.owner == playerName for x in self.getTerritoriesByContinent(continentName))

    def getContinentBonus(self, playerName):
        unitCount = 0

        for continent in self.continents.values():
            unitCount += continent.unitBonus if self.isContinentControlledByPlayer(continent.name, playerName) else 0

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
        if (self.territoryContinentCache == None):
            self.territoryContinentCache = {}
            for continent in self.continents.values():
                self.territoryContinentCache[continent.name] = []
            for territory in self.territories.values():
                self.territoryContinentCache[territory.continent].append(territory)
        return self.territoryContinentCache[continentName]

    def moveArmies(self, supplyIndex, receiveIndex, amount):
        self.territories[supplyIndex].addArmy(-amount)
        self.territories[receiveIndex].addArmy(amount)

    def attackTerritory(self, attackIndex, defendIndex, minimumRemainingPercent, attackArmyMax, defendArmyMax, atkSys):
        if (attackIndex == None or defendIndex == None):
            # rm print(f"{self.name} chose not to attack this turn")
            return None

        attackingTerritory = self.territories[attackIndex]
        defendingTerritory = self.territories[defendIndex]

        attackingArmies = attackingTerritory.getArmy() - 1  # Keep one remaining on the territory
        defendingArmies = defendingTerritory.getArmy()

        minimumAmountRemaining = math.floor(attackingArmies * minimumRemainingPercent)
        attackArmyMax = round(attackArmyMax)
        defendArmyMax = round(defendArmyMax)
        attackArmyMax = max(1, min(attackArmyMax, 3)) # Clamp value from 1-3
        defendArmyMax = max(1, min(defendArmyMax, 2)) # Clamp value from 1-3

        # Actually perform the attack
        attackResult = atkSys.attack(attackingArmies, defendingArmies, minimumAmountRemaining, attackArmyMax, defendArmyMax)

        # If the attack was successful, change ownership
        attackSuccessful = (attackResult.defenders == 0)
        if (attackSuccessful):
            defendingTerritory.owner = attackingTerritory.owner

            # Keep any remaining armies
            attackingTerritory.setArmy(attackResult.attackers)
            # Take an attacking army and place it on the new territory
            defendingTerritory.setArmy(1)
        else:
            # Keep any remaining armies
            # Don't forget about the 1 that wasn't allowed to leave
            attackingTerritory.setArmy(attackResult.attackers + 1)
            # Let the defenders keep their remaining armies
            defendingTerritory.setArmy(attackResult.defenders)
        return attackResult

