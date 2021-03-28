from Map import Map
import random
from Game import Game
from Territory import Territory
from Agent import Agent


def setupGameBoard(agentList, initialUnits, map):
    agentListSize = len(agentList)
    initialUnits *= agentListSize
    agentIndex = 0
    for i in range(initialUnits):
        agentList[agentIndex].placeUnitSetup(map)
        agentIndex += 1
        agentIndex = agentIndex % agentListSize


game = Game()
map = Map()
map.readMapData("MapData.txt")

agents = [Agent("Jake"), Agent("Xander"), Agent("Sabrina"), Agent("Rusty")]

setupGameBoard(agents, 30, map)

game.showWindow(map)
