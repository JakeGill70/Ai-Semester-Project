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
from RiskGame import RiskGame


class Tournament():
    @staticmethod
    def playTournament(population, map, generationCount=0, turnCountFilePathName=""):
        populationSize = len(population)
        remainingPercent = 0.25
        loserList = []
        master_loserList = []
        t = 0
        windowName = ""
        while(len(population) > populationSize * remainingPercent):
            matchUps = population.getMatchGroups(4)
            winnerList = []
            loserList = []
            turnCountList = []
            m = 0
            t += 1
            for match in matchUps:
                m += 1
                Logger.message(MessageTypes.MatchStartNotice, f"Gen {generationCount}, Tier {t}, Match {m}")
                windowName = f"RISK: Gen {generationCount}, Tier {t}, Match {m}"
                matchWinners, matchLosers, turnCount = RiskGame.playGame(match, map, True, windowName)
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
            if(turnCountFilePathName):
                Tournament.writeTurnCountFile(turnCountList, turnCountFilePathName)

    @staticmethod
    def writeTurnCountFile(turnCountList, turnCountFilePathName):
        turnCountList.sort()
        tc_min = turnCountList[0]
        tc_max = turnCountList[-1]
        tc_mean = sum(turnCountList)/len(turnCountList)
        tc_median = turnCountList[math.ceil(len(turnCountList)/2)]
        tc_std_dev = math.sqrt(sum((tc-tc_mean)**2 for tc in turnCountList)/len(turnCountList))
        f = open(turnCountFilePathName, "at+")
        f.write(f"{tc_min},{tc_max},{tc_mean},{tc_median},{tc_std_dev}\n")
        f.close()

    @staticmethod
    def playMultipleTournaments(
            map, populationSize, generationCount, lowMutationMod, highMutationMod, agentOutputDirectory,
            turnCountFilePathName):
        # Define inner function to interpolate between the low & high mutation modifiers
        def interpolate(x, y, t):
            return x*(1-t) + y*t

        # Ensure that the file directory for output exists
        os.makedirs(os.path.abspath(agentOutputDirectory))

        # Write turn file CSV headers
        f = open(turnCountFilePathName, "at+")
        f.write("min, max, mean, median, std dev\n")
        f.close()

        # Create initial population
        generalPopulation = Population(populationSize)
        generalPopulation.initAllAgents()

        # Play the multiple tournaments to create the different generations
        for i in range(generationCount):
            Logger.message(MessageTypes.GenerationStartNotice, f"GENERATION {int(i)}")
            # Play tournament
            Tournament.playTournament(generalPopulation, map, i, turnCountFilePathName)

            # Write out average agent values
            avgGenAgent = generalPopulation.getAverageAgent(name=f"Gen{i:05d} Mean Agent")
            AgentReader.writeAgent(f"{agentOutputDirectory}Gen{(i):05d}.json", avgGenAgent)

            # Create the next generation within the population
            mutationMultiplier = interpolate(highMutationMod, lowMutationMod, (i/generationCount))
            generalPopulation.generateNextGeneration(mutationMultiplier)
