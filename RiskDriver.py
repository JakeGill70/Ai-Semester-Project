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


def attackUntilUnfavorable(agent, map, atkSys):
    while(True):
        pickTerritoryResult = agent.pickTerritoryForAttack(map, atkSys)
        attackResult = agent.attackTerritory(pickTerritoryResult, map, atkSys)
        if(attackResult):
            print(f"{agent.name}'s attack from #{pickTerritoryResult.attackIndex} to #{pickTerritoryResult.defendIndex} was {'successful' if (attackResult.defenders == 0) else 'unsuccessful'}.")
        else:
            print(f"{agent.name} decided to stop attacking.")
            break


def playGame(agents):
    game = Game()
    map = Map()
    map.readMapData("MapData.txt")
    map.updateContinentCount()
    atkSys = AttackSystem()
    winners = []

    setupGameBoard(agents, 30, map)

    print("Presenting initial map")
    game.showWindow(map)

    MAX_TURN_COUNT = 1000
    GRAPH_UPDATE_FREQUENCY = 10
    turnCount = 0
    agentIndex = -1
    while(turnCount < MAX_TURN_COUNT):
        # Print out turn count update
        turnCount += 1
        agentIndex = (agentIndex + 1) % len(agents)
        print(f"=====================")
        print(f"    Turn: {turnCount} : {agents[agentIndex].name}")
        print(f"=====================")

        # Place Units
        newUnits = map.getNewUnitCountForPlayer(agents[agentIndex].name)
        for i in range(newUnits):
            placementIndex = agents[agentIndex].placeUnit(map)
            print(f"{agents[agentIndex].name} placed a unit at #{placementIndex}.")

        # Attack
        attackUntilUnfavorable(agents[agentIndex], map, atkSys)

        # Move
        pickMovementResult = agents[agentIndex].pickTerritoryForMovement(map)
        if(pickMovementResult):
            map.moveArmies(pickMovementResult.supplyIndex, pickMovementResult.receiveIndex,
                           pickMovementResult.transferAmount)
            print(f"{agents[agentIndex].name} moved {pickMovementResult.transferAmount} units from #{pickMovementResult.supplyIndex} to #{pickMovementResult.receiveIndex}.")

        # Period update
        if(turnCount % GRAPH_UPDATE_FREQUENCY == 0):
            game.showWindow(map, 0.1)

        # Remove defeated players
        agentsToRemove = []
        for agent in agents:
            if(len(map.getTerritoriesByPlayer(agent.name)) == 0):
                print(f"{agent.name} has been defeated by {agents[agentIndex].name}!")
                agentsToRemove.append(agent)
                game.showWindow(map, 1.0)
                # input()
        for agent in agentsToRemove:
            agents.remove(agent)

        # Check for winner
        if(len(agents) == 1):
            print(f"{agents[0].name} is the winner!")
            winners.append(agents[0])
            break

    if(turnCount >= MAX_TURN_COUNT):
        print(f"Max turn limit reached, determining winner based on territory, using army count as tie breaker.")
        # TODO: Do like this print statement says :P

        # Sort remaining agents by number of territories
        agents.sort(key=lambda x: len(map.getTerritoriesByPlayer(x.name)))

        # if there is a tie...
        if(len(map.getTerritoriesByPlayer(agents[0].name)) == len(map.getTerritoriesByPlayer(agents[1].name))):
            print("Tie!")
            # Reduce agents to just those with the same number of territories
            agents = [x for x in agents if len(map.getTerritoriesByPlayer(x.name)) ==
                      len(map.getTerritoriesByPlayer(agents[0].name))]
            # Sort remaining agents by number of armies
            sassy = [map.getTotalArmiesByPlayer(x.name) for x in agents]
            agents.sort(key=lambda x: map.getTotalArmiesByPlayer(x.name))
            # if there is still a tie...
            if(map.getTotalArmiesByPlayer(agents[0].name) == map.getTotalArmiesByPlayer(agents[1].name)):
                # Reduce agents to just those with the same number of armies
                agents = [x for x in agents if map.getTotalArmiesByPlayer(
                    x.name) == map.getTotalArmiesByPlayer(agents[0].name)]
                # Return all winners that are tied
                winners = agents
            else:
                # There is not still a tie
                winners.append(agents[0])
        else:
            # There is not a tie
            winners.append(agents[0])

        print(f"Winner(s): {[x.name for x in winners]}")

    print("Presenting final map")
    game.showWindow(map, 1.0)

    return winners


gameAgents = [Agent("Jake"), Agent("Xander"), Agent("Sabrina"), Agent("Rusty")]
playGame(gameAgents)
