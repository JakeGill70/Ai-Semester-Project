import sys
from Territory import Territory
import math


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

    def getPositions(self):
        positions = {}
        for territory in self.territories:
            positions[territory.index] = territory.position
        return positions

    def getTotalArmiesByPlayer(self, playerName):
        return sum([x for x.army in self.getTerritoriesByPlayer(playerName)])

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
        territory = self.territories[territoryId]
        if(territory.owner and territory.owner != playerName):
            raise Exception(f"Player '{playerName}' is \
                        trying to place {amount} armies \
                        at {territoryId} controlled by \
                        {self.owners[territoryId]}")
        else:
            territory.army += amount
            territory.owner = playerName

    def readMapData(self, filePath):
        currentContinent = ""
        f = open(filePath, "r")
        for line in f:
            # Ignore comment lines
            if(line[0] == "#"):
                continue

            # Process continent lines
            if(line.strip().startswith("continent")):
                try:
                    currentContinent = line.split("=")[1].strip()
                    continue
                except IndexError:
                    print(f"Malform line in mapdata: '{line}'", file=sys.stderr)
                    continue

            # Process data lines
            try:
                data = line.split(":")
                index = int(data[0].strip())
                connections = [int(x.strip()) for x in data[1].split(",")]
                position = tuple([int(x.strip()) for x in data[2].split(",")])
                self.territories[index] = Territory(index, connections, currentContinent, position)
            except IndexError:
                print(f"Malform line in mapdata: '{line}'", file=sys.stderr)
                continue
        f.close()

        # Verify all connections are bi-directional
        for territory in self.territories.values():
            for connectingIndex in territory.connections:
                connectingTerritory = self.territories[connectingIndex]
                if(territory.index not in connectingTerritory.connections):
                    print(
                        f"Uni-directional connection found. {index} is connected to {i}, but {i} is not connected to {index}",
                        file=sys.stderr)

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
