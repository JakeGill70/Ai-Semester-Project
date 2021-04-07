from Map import Map
import random
from Game import Game
from Territory import Territory
from Agent import Agent
from AttackSystem import AttackSystem


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
map.updateContinentCount()
atkSys = AttackSystem()

agents = [Agent("Jake"), Agent("Xander"), Agent("Sabrina"), Agent("Rusty")]

setupGameBoard(agents, 30, map)

pickTerritoryResult = agents[0].pickTerritoryForAttack(map, atkSys)
agents[0].attackTerritory(pickTerritoryResult, map, atkSys)


game.showWindow(map)
