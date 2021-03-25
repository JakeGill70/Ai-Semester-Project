from Map import Map
import random
from Game import Game
from Territory import Territory

game = Game()
map = Map()
map.readMapData("MapData.txt")

players = ["A", "B", "C", "D"]
count = 30

c = 0

for i in range(count):
    for player in players:
        emptyTerritories = map.getTerritoriesByPlayer("")
        myTerritories = map.getTerritoriesByPlayer(player)
        selectedTerritory = None
        if(len(emptyTerritories) > 0):
            selectedTerritory = random.choice(emptyTerritories)
        else:
            selectedTerritory = random.choice(myTerritories)
        map.placeArmy(player, 1, selectedTerritory.index)
        c += 1

print(c)

game.showWindow(map)
