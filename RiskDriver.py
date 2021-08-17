from Map import Map
import random
from Game import Game
from Territory import Territory
from Agent import Agent
from AttackSystem import AttackSystem
from Population import Population
from MapReader import MapReader


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

    setupGameBoard(agents, 30, map)

    if(showGame):
        print("Presenting initial map")
        game.showWindow(map, 0.5)

    # Each player should get 100 turns
    turnCount = 0
    turnCountPerPlayer = 10
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
            game.showWindow(map, 0.1, tmpWindowName)

        # Remove defeated players
        agentsToRemove = []
        for agent in agents:
            if(len(map.getTerritoriesByPlayer(agent.name)) == 0):
                agentsToRemove.append(agent)
                if(showGame):
                    print(f"{agent.name} has been defeated by {agents[agentIndex].name}!")
                    game.showWindow(map, 0.5, (f"RISK: {agent.name} has been defeated by {agents[agentIndex].name}!"))
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

    if(turnCount >= maxTurnCount):
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

    return (winners, losers)


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
        m = 0
        t += 1
        for match in matchUps:
            m += 1
            print("\n\n\nGeneration", generationCount, "Match ", m, ", Tier ", t, "\n\n\n\n")
            windowName = f"RISK: Gen {generationCount}, Tier {t}, Match {m}"
            matchWinners, matchLosers = playGame(match, True, windowName)
            winnerList += matchWinners
            loserList += matchLosers
        # Clear the gene pool
        population.clear()
        # Add winners back into the gene pool
        population.addAgents(winnerList)
        # Add losers back into the gene pool, if they have not lost before
        population.addAgents([loser for loser in loserList if loser not in master_loserList])
        # Add losers to big list of all losers
        master_loserList += loserList


GENERATION_COUNT = 5
POPULATION_SIZE = 20
generalPopulation = Population(POPULATION_SIZE)
generalPopulation.initAllAgents()
for i in range(GENERATION_COUNT):
    print(f"\n\n<<< GENERATION {int(i)} >>>\n\n")
    playTournament(generalPopulation, i)
    generalPopulation.generateNextGeneration()

for agent in generalPopulation.allAgents:
    print(agent.name + "'s stats:" + agent.stats())
