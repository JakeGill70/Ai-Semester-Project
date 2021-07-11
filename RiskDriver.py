from Map import Map
import random
from Game import Game
from Territory import Territory
from Agent import Agent
from AttackSystem import AttackSystem
from Population import Population


def setupGameBoard(agentList, initialUnits, map):
    agentListSize = len(agentList)
    initialUnits *= agentListSize
    agentIndex = 0
    for i in range(initialUnits):
        agentList[agentIndex].placeUnitSetup(map)
        agentIndex += 1
        agentIndex = agentIndex % agentListSize


def attackUntilUnfavorable(agent, map, atkSys, showGame=True):
    while(True):
        pickTerritoryResult = agent.pickTerritoryForAttack(map, atkSys)
        attackResult = agent.attackTerritory(pickTerritoryResult, map, atkSys)
        if(showGame):
            if(attackResult):
                print(f"{agent.name}'s attack from #{pickTerritoryResult.attackIndex} to #{pickTerritoryResult.defendIndex} was {'successful' if (attackResult.defenders == 0) else 'unsuccessful'}.")
            else:
                print(f"{agent.name} decided to stop attacking.")
                break


def playGame(agents, showGame=True):
    game = Game()
    map = Map()
    map.readMapData("MapData.txt")
    map.updateContinentCount()
    atkSys = AttackSystem()
    winners = []
    losers = []

    setupGameBoard(agents, 30, map)

    if(showGame):
        print("Presenting initial map")
        game.showWindow(map, 0.5)

    MAX_TURN_COUNT = 1000
    GRAPH_UPDATE_FREQUENCY = 10
    turnCount = 0
    agentIndex = -1
    while(turnCount < MAX_TURN_COUNT):
        # Print out turn count update
        turnCount += 1
        agentIndex = (agentIndex + 1) % len(agents)
        if(showGame):
            print(f"=====================")
            print(f"    Turn: {turnCount} : {agents[agentIndex].name}")
            print(f"=====================")

        # Place Units
        newUnits = map.getNewUnitCountForPlayer(agents[agentIndex].name)
        for i in range(newUnits):
            placementIndex = agents[agentIndex].placeUnit(map)
            if(showGame):
                print(f"{agents[agentIndex].name} placed a unit at #{placementIndex}.")

        # Attack
        attackUntilUnfavorable(agents[agentIndex], map, atkSys, showGame)

        # Move
        pickMovementResult = agents[agentIndex].pickTerritoryForMovement(map)
        if(pickMovementResult):
            map.moveArmies(pickMovementResult.supplyIndex, pickMovementResult.receiveIndex,
                           pickMovementResult.transferAmount)
            if(showGame):
                print(f"{agents[agentIndex].name} moved {pickMovementResult.transferAmount} units from #{pickMovementResult.supplyIndex} to #{pickMovementResult.receiveIndex}.")

        # Period update
        if(showGame and turnCount % GRAPH_UPDATE_FREQUENCY == 0):
            game.showWindow(map, 0.1)

        # Remove defeated players
        agentsToRemove = []
        for agent in agents:
            if(len(map.getTerritoriesByPlayer(agent.name)) == 0):
                agentsToRemove.append(agent)
                if(showGame):
                    print(f"{agent.name} has been defeated by {agents[agentIndex].name}!")
                    game.showWindow(map, 0.5)
        for agent in agentsToRemove:
            losers.append(agent)
            agents.remove(agent)

        # Check for winner
        if(len(agents) == 1):
            if(showGame):
                print(f"{agents[0].name} is the winner!")
            winners.append(agents[0])
            break

    if(turnCount >= MAX_TURN_COUNT):
        if(showGame):
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

        # Change any non-winners to losers
        for a in agents:
            if(a not in winners):
                losers.append(a)

        if(showGame):
            print(f"Winner(s): {[x.name for x in winners]}")
            print(f"Losers: {[x.name for x in losers]}")

    if(showGame):
        print("Presenting final map")
        game.showWindow(map, 1.0)

    return (winners, losers)


POPULATION_SIZE = 500
generalPopulation = Population(POPULATION_SIZE)
generalPopulation.initAllAgents()
loserList = []
master_loserList = []
t = 0
while(len(generalPopulation) > POPULATION_SIZE/4):
    matchUps = generalPopulation.getMatchGroups(4)
    winnerList = []
    loserList = []
    m = 0
    t += 1
    for match in matchUps:
        m += 1
        print("\n\n\n\nMatch ", m, ", Tier ", t, "\n\n\n\n\n")
        matchWinners, matchLosers = playGame(match, True)
        winnerList += matchWinners
        loserList += matchLosers
    # Clear the gene pool
    generalPopulation.clear()
    # Add winners back into the gene pool
    generalPopulation.addAgents(winnerList)
    # Add losers back into the gene pool, if they have not lost before
    generalPopulation.addAgents([loser for loser in loserList if loser not in master_loserList])
    # Add losers to big list of all losers
    master_loserList += loserList


print("Winners: " + str(len(winnerList)))
print("Losers: " + str(len(loserList)))

# gameAgents = [Agent("Jake"), Agent("Xander"), Agent("Sabrina"), Agent("Rusty")]
# winners, losers = playGame(gameAgents, True)
# print("Winners: ")
# print(winners)
# print("Losers: ")
# print(losers)
