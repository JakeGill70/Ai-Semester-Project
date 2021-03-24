import sys
from Territory import Territory


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

    def getPositions(self):
        positions = {}
        for territory in self.territories:
            positions[territory.index] = territory.position
        return positions

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
