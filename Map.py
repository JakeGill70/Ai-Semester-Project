import sys


class Map():
    def __init__(self):
        super().__init__()
        self.mapData = {}
        self.continents = {}
        self.positionData = {}
        # TODO: Make these readable from the MapData instead of hardcoded
        self.continentColors = {
            "North America": (255, 255, 0),  # Yellow
            "South America": (255, 0, 0),  # Red
            "Europe": (200, 200, 200),  # Grey
            "Africa": (0, 255, 0),  # Green
            "Asia": (0, 0, 255),  # Blue
            "Australia": (255, 0, 255)  # Pink
        }

    def getContinentOfIndex(self, index):
        for key, value in self.continents.items():
            if(index in value):
                return key

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
                    self.continents[currentContinent] = []
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
                self.mapData[index] = connections
                self.continents[currentContinent].append(index)
                self.positionData[index] = position
            except IndexError:
                print(f"Malform line in mapdata: '{line}'", file=sys.stderr)
                continue
        f.close()

        # Verify all connections are bi-directional
        for index, connections in self.mapData.items():
            for i in connections:
                if(index not in self.mapData[i]):
                    print(
                        f"Uni-directional connection found. {index} is connected to {i}, but {i} is not connected to {index}",
                        file=sys.stderr)
