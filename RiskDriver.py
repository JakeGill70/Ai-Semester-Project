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
from Logger import Logger, MessageTypes
from AgentReader import AgentReader
from Tournament import Tournament


GENERATION_COUNT = 1500
POPULATION_SIZE = 256
HIGH_MUTATION_MODIFIER = 1.75
LOW_MUTATION_MODIFIER = 0.5
AGENT_OUTPUT_DIRECTORY_PATH = f"./Average Agents/{datetime.now().strftime('%Y-%m-%d-%I-%M%p')}/"
TURN_COUNT_FILE_NAME = f"{AGENT_OUTPUT_DIRECTORY_PATH}turnCount.txt"

map = MapReader.readMap("./NewMapData.json")

Tournament.playMultipleTournaments(map, POPULATION_SIZE, GENERATION_COUNT, LOW_MUTATION_MODIFIER,
                                   HIGH_MUTATION_MODIFIER, AGENT_OUTPUT_DIRECTORY_PATH, TURN_COUNT_FILE_NAME)
