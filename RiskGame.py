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


class RiskGame():
    @staticmethod
    def setupGameBoard(agentList, initialUnits, map):
        agentListSize = len(agentList)
        initialUnits *= agentListSize
        agentIndex = 0

        # guarantee that there is at least enough units to cover the map
        # This can sometimes happen if there is only 1 player. The game board
        # must still be setup correctly before they can end their turn and
        # the game logic recognize that they are the only remaining player
        # at the end of that first turn.
        if(initialUnits < map.getTerritoryCount()):
            initialUnits = map.getTerritoryCount()

        for i in range(initialUnits):
            agentList[agentIndex].placeUnitSetup(map)
            agentIndex += 1
            agentIndex = agentIndex % agentListSize

    @staticmethod
    def attackUntilUnfavorable(agent, map, atkSys, showGame=True):
        while(True):
            pickTerritoryResult = agent.pickTerritoryForAttack(map, atkSys)
            attackResult = agent.attackTerritory(pickTerritoryResult, map, atkSys)
            if(showGame):
                if(attackResult):
                    Logger.message(
                        MessageTypes.AttackResult,
                        f"{agent.name}'s attack from #{pickTerritoryResult.attackIndex} to #{pickTerritoryResult.defendIndex} was {'successful' if (attackResult.defenders == 0) else 'unsuccessful'}.")
                else:
                    Logger.message(MessageTypes.AttackStopNotice, "{agent.name} decided to stop attacking.")
                    break

    @staticmethod
    def getLosingPlayers(agents, currentAgentTurn, map, game, showGame=True):
        agentsToRemove = []
        for agent in agents:
            if(len(map.getTerritoriesByPlayer(agent.name)) == 0):
                agentsToRemove.append(agent)
                if(showGame):
                    Logger.message(MessageTypes.PlayerDefeatedNotice,
                                   f"{agent.name} has been defeated by {currentAgentTurn.name}!")
                    game.showWindow(
                        map, 0.1, (f"RISK: {agent.name} has been defeated by {currentAgentTurn.name}!"))
        return agentsToRemove

    @staticmethod
    def getWinningPlayers(agents, map, turnCount, maxTurnCount, showGame=True):
        winners = []
        losers = []
        # Only 1 winner left, so they must be it
        if(len(agents) == 1):
            if(showGame):
                Logger.message(MessageTypes.PlayerVictoryNotice, f"{agents[0].name} is the winner!")
            winners.append(agents[0])

        if(turnCount >= maxTurnCount and len(agents) > 1):

            if(showGame):
                Logger.message(
                    MessageTypes.TurnLimitReachedNotice,
                    f"Max turn limit reached, determining winner based on territory, using army count as tie breaker.")

            # Sort remaining agents by number of territories
            agents.sort(key=lambda x: len(map.getTerritoriesByPlayer(x.name)))

            # if there is a tie...
            if(len(map.getTerritoriesByPlayer(agents[0].name)) == len(map.getTerritoriesByPlayer(agents[1].name))):
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
                Logger.message(MessageTypes.GameResults,
                               f"Winner(s): {[x.name for x in winners]}\nLosers: {[x.name for x in losers]}")

        return (winners, losers)

    @staticmethod
    def playGame(agents, map, showGame=True, windowName="RISK"):
        game = Game()
        map = map.getCopy()
        atkSys = AttackSystem()
        winners = []
        losers = []

        Logger.message(MessageTypes.GameStartNotice, f"Playing Game: {[agent.name for agent in agents]}")
        if(len(agents) != len(set([agent.name for agent in agents]))):
            Logger.message(MessageTypes.DuplicatePlayerWarning,
                           f"Error: Duplicate player names: {[agent.name for agent in agents]}", file=sys.stderr)
            return ([], [])

        RiskGame.setupGameBoard(agents, 30, map)

        if(showGame):
            Logger.message(MessageTypes.GuiMirror, "Presenting initial map")
            game.showWindow(map, 0.5)

        # Each player should get 100 turns
        turnCount = 0
        turnCountPerPlayer = 100
        maxTurnCount = len(agents) * turnCountPerPlayer
        GRAPH_UPDATE_FREQUENCY = 10
        agentIndex = -1
        tmpWindowName = ""
        while(turnCount < maxTurnCount and not bool(winners)):
            # Print out turn count update
            turnCount += 1
            agentIndex = (agentIndex + 1) % len(agents)
            tmpWindowName = windowName + f", turn {turnCount}"
            if(showGame):
                Logger.message(
                    MessageTypes.TurnStartNotice,
                    f"=====================\nTurn: {turnCount} : {agents[agentIndex].name}\n=====================")

            # Place Units
            newUnits = map.getNewUnitCountForPlayer(agents[agentIndex].name)
            for i in range(newUnits):
                placementIndex = agents[agentIndex].placeUnit(map)
                if(showGame):
                    Logger.message(MessageTypes.UnitPlacementNotice,
                                   f"{agents[agentIndex].name} placed a unit at #{placementIndex}.")

            # Attack
            RiskGame.attackUntilUnfavorable(agents[agentIndex], map, atkSys, showGame)

            # Move
            pickMovementResult = agents[agentIndex].pickTerritoryForMovement(map)
            if(pickMovementResult):
                map.moveArmies(pickMovementResult.supplyIndex, pickMovementResult.receiveIndex,
                               pickMovementResult.transferAmount)
                if(showGame):
                    Logger.message(
                        MessageTypes.UnitMovementNotice,
                        f"{agents[agentIndex].name} moved {pickMovementResult.transferAmount} units from #{pickMovementResult.supplyIndex} to #{pickMovementResult.receiveIndex}.")

            # Period update
            if(showGame and turnCount % GRAPH_UPDATE_FREQUENCY == 0):
                game.showWindow(map, 0.01, tmpWindowName)

            # Remove defeated players
            agentsToRemove = RiskGame.getLosingPlayers(agents, agents[agentIndex], map, game, showGame)

            for agent in agentsToRemove:
                # TODO: Remove that player agent's remaining turns
                #   To ensure that each player uses the proper number of turns per player.
                losers.append(agent)
                agents.remove(agent)

            # Check for winners
            gameWinners, gameLosers = RiskGame.getWinningPlayers(agents, map, turnCount, maxTurnCount, showGame)
            winners += gameWinners
            losers += gameLosers

        # Check for winners
        gameWinners, gameLosers = RiskGame.getWinningPlayers(agents, map, turnCount, maxTurnCount, showGame)
        winners += gameWinners
        losers += gameLosers

        # Remove duplicates
        winners = list(set(winners))
        losers = list(set(losers))

        if(showGame):
            Logger.message(MessageTypes.GuiMirror, "Presenting final map")
            game.showWindow(map, 1.0, (windowName + ", final"))

        return (winners, losers, turnCount)
