from Map import Map
from MapReader import MapReader
from Agent import Agent
from AgentReader import AgentReader
from Logger import Logger, MessageTypes
from Tournament import Tournament
from RiskGame import RiskGame
from datetime import datetime

if __name__ == '__main__':
    EXAMPLE = 4

    GENERATION_COUNT = 1500
    POPULATION_SIZE = 256
    HIGH_MUTATION_MODIFIER = 1.75
    LOW_MUTATION_MODIFIER = 0.5
    AGENT_OUTPUT_DIRECTORY_PATH = f"./Average Agents/{datetime.now().strftime('%Y-%m-%d-%I-%M%p')}/"
    TURN_COUNT_FILE_NAME = f"{AGENT_OUTPUT_DIRECTORY_PATH}turnCount.txt"

    map = MapReader.readMap("./NewMapData.json")

    if (EXAMPLE == 1):
        Tournament.playMultipleTournaments(map.getCopy(), POPULATION_SIZE,
                                           GENERATION_COUNT,
                                           LOW_MUTATION_MODIFIER,
                                           HIGH_MUTATION_MODIFIER,
                                           AGENT_OUTPUT_DIRECTORY_PATH,
                                           TURN_COUNT_FILE_NAME)

    elif (EXAMPLE == 2):
        RiskGame.playGame(AgentReader.readSampleAgents(), map.getCopy())

    elif (EXAMPLE == 3):
        winCounts = {"Jacob": 0, "Sabrina": 0, "Jamey": 0, "Rusty": 0}
        for i in range(100):
            winners, losers, turnCount = RiskGame.playGame(
                AgentReader.readSampleAgents(), map.getCopy())
            for winner in winners:
                winCounts[winner.name] += 1

        for player in winCounts.keys():
            print(f"{player}'s Wins: {winCounts[player]}")

    elif (EXAMPLE == 4):
        RiskGame.playGameMax(AgentReader.readSampleAgents(), map.getCopy())
