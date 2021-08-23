from Map import Map
import random
from Game import Game
from Territory import Territory
from Agent import Agent
from AttackSystem import AttackSystem
from Population import Population
from MapReader import MapReader
from datetime import datetime
import os
import math

# TODO: Break a lot of this off into a "Tournament" or a "RiskGame" class, or both.
#   This code is growing way beyond what should be in a simple driver class.


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


def playGame(agents, showGame=True, windowName="RISK"):
    game = Game()
    map = MapReader.readMap("./NewMapData.json")
    atkSys = AttackSystem()
    winners = []
    losers = []

    print(f"Playing Game: {[agent.name for agent in agents]}")
    if(len(agents) != len(set([agent.name for agent in agents]))):
        print(f"Error: Duplicate player names: {[agent.name for agent in agents]}", file=sys.stderr)
        return ([], [])

    setupGameBoard(agents, 30, map)

    if(showGame):
        print("Presenting initial map")
        game.showWindow(map, 0.5)

    # Each player should get 100 turns
    turnCount = 0
    turnCountPerPlayer = 100
    maxTurnCount = len(agents) * turnCountPerPlayer
    GRAPH_UPDATE_FREQUENCY = 10
    agentIndex = -1
    tmpWindowName = ""
    while(turnCount < maxTurnCount):
        # Print out turn count update
        turnCount += 1
        agentIndex = (agentIndex + 1) % len(agents)
        tmpWindowName = windowName + f", turn {turnCount}"
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
            game.showWindow(map, 0.01, tmpWindowName)

        # Remove defeated players
        agentsToRemove = []
        for agent in agents:
            if(len(map.getTerritoriesByPlayer(agent.name)) == 0):
                agentsToRemove.append(agent)
                if(showGame):
                    print(f"{agent.name} has been defeated by {agents[agentIndex].name}!")
                    game.showWindow(map, 0.1, (f"RISK: {agent.name} has been defeated by {agents[agentIndex].name}!"))
        for agent in agentsToRemove:
            # TODO: Remove that player agent's remaining turns
            #   To ensure that each player uses the proper number of turns per player.
            losers.append(agent)
            agents.remove(agent)

        # Check for winner
        if(len(agents) == 1):
            if(showGame):
                print(f"{agents[0].name} is the winner!")
            winners.append(agents[0])
            break

    if(turnCount >= maxTurnCount and len(agents) > 1):

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
        game.showWindow(map, 1.0, (windowName + ", final"))

    return (winners, losers, turnCount)


def playTournament(population, generationCount=0):
    populationSize = len(population)
    loserList = []
    master_loserList = []
    t = 0
    windowName = ""
    while(len(population) > populationSize/4):
        matchUps = population.getMatchGroups(4)
        winnerList = []
        loserList = []
        turnCountList = []
        m = 0
        t += 1
        for match in matchUps:
            m += 1
            print("\n\n\nGeneration", generationCount, "Match ", m, ", Tier ", t, "\n\n\n\n")
            windowName = f"RISK: Gen {generationCount}, Tier {t}, Match {m}"
            matchWinners, matchLosers, turnCount = playGame(match, True, windowName)
            winnerList += matchWinners
            loserList += matchLosers
            turnCountList.append(turnCount)
        # Clear the gene pool
        population.clear()
        # Add winners back into the gene pool
        population.addAgents(winnerList)
        # Add losers back into the gene pool, if they have not lost before
        population.addAgents([loser for loser in loserList if loser not in master_loserList])
        # Add losers to big list of all losers
        master_loserList += loserList
        # TODO: Get the file name by parameter instead of using a global
        # Also make it not print out if no file name is given
        # Also, also, should this even be done here? I think it should return the
        # turn count and then have the driver deal with writing the output
        turnCountList.sort()
        tc_min = turnCountList[0]
        tc_max = turnCountList[-1]
        tc_mean = sum(turnCountList)/len(turnCountList)
        tc_median = turnCountList[math.ceil(len(turnCountList)/2)]
        tc_std_dev = math.sqrt(sum((tc-tc_mean)**2 for tc in turnCountList)/len(turnCountList))
        f = open(TURN_COUNT_FILE_NAME, "at+")
        f.write(f"{tc_min},{tc_max},{tc_mean},{tc_median},{tc_std_dev}\n")
        f.close()


def interpolate(x, y, t):
    return x*(1-t) + y*t


GENERATION_COUNT = 500
POPULATION_SIZE = 100
HIGH_MUTATION_MODIFIER = 1.75
LOW_MUTATION_MODIFIER = 0.5
AGENT_OUTPUT_DIRECTORY_PATH = f"./Average Agents/{datetime.now().strftime('%Y-%m-%d-%I-%M%p')}/"
TURN_COUNT_FILE_NAME = f"{AGENT_OUTPUT_DIRECTORY_PATH}turnCount.txt"

os.makedirs(os.path.abspath(AGENT_OUTPUT_DIRECTORY_PATH))

f = open(TURN_COUNT_FILE_NAME, "at+")
f.write("min, max, mean, median, std dev\n")
f.close()

generalPopulation = Population(POPULATION_SIZE)
generalPopulation.initAllAgents()
for i in range(GENERATION_COUNT):
    print(f"\n\n<<< GENERATION {int(i)} >>>\n\n")
    playTournament(generalPopulation, i)

    # TODO: Pull this average agent output to separate method
    f = open(f"{AGENT_OUTPUT_DIRECTORY_PATH}Gen{(i):03d}.json", "wt+")
    f.write(generalPopulation.getAverageAgent(name=f"Gen{i:03d} Mean Agent").toJSON())
    f.close()

    mutationMultiplier = interpolate(HIGH_MUTATION_MODIFIER, LOW_MUTATION_MODIFIER, (i/GENERATION_COUNT))
    generalPopulation.generateNextGeneration(mutationMultiplier)

for agent in generalPopulation.allAgents:
    print(agent.name + "'s stats:" + agent.stats())
