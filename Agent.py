class AgentCharacteristic:
    def __init__(self, value, description):
        self.value = value
        self.description = description

    def __int__(self):
        return self.value


class Agent:
    def __init__(self, name):
        self.name = name
        self.characteristics = {
            "Placement": {
                "Anywhere": AgentCharacteristic(3, "Placing a unit anywhere"),
                "Enemy Adjacent": AgentCharacteristic(5, "Placing a unit on a country connected to a country controlled by a different player"),
                "Border Adjacent": AgentCharacteristic(8, "Placing a unit in a country that borders a country in a different continent"),
                "Connection Bias": AgentCharacteristic(1, "Placing a unit on a country with connections to multiple other countries, +value per connection"),
                "Placement Bias Multiplier": AgentCharacteristic(0.5, "Placing a unit where there already are other units, *value per army")
            },
            "Preference": {
                "Larger": AgentCharacteristic(1, "Preference to attack larger players"),
                "Smaller": AgentCharacteristic(1, "Preference to attack smaller players"),
                "Aggression": AgentCharacteristic(1, "Preferrence for aggressive actions"),
                "Risky": AgentCharacteristic(1, "Preference for risky actions"),
                "Safe": AgentCharacteristic(1, "Preference for safe actions")
            }
        }

    def getTerritoryDataBorderAdjacent(self, territoryIndex, map):
        territoryData = map.territories[territoryIndex]
        adjacentTerritoryData = [map.territories[ti] for ti in territoryData.connections
                                 if map.territories[ti].continent != territoryData.continent]
        return adjacentTerritoryData

    def getTerritoryDataEnemyAdjacent(self, territoryIndex, map):
        territoryData = map.territories[territoryIndex]
        adjacentTerritoryData = [map.territories[ti] for ti in territoryData.connections
                                 if map.territories[ti].owner != self.name
                                 and map.territories[ti].owner != ""]
        return adjacentTerritoryData

    def pickTerritory(self, possibleTerritoryData, map):
        score = 0
        bestScore = -1
        bestIndex = -1
        for territoryData in possibleTerritoryData:
            score = 0
            # Calculate placement score based on placement settings
            score += self.characteristics["Placement"]["Anywhere"].value
            enemyAdjacentsData = self.getTerritoryDataEnemyAdjacent(territoryData.index, map)
            score += self.characteristics["Placement"]["Enemy Adjacent"].value if self.getTerritoryDataEnemyAdjacent(
                territoryData.index, map) else 0
            score += self.characteristics["Placement"]["Border Adjacent"].value if self.getTerritoryDataEnemyAdjacent(
                territoryData.index, map) else 0
            score += self.characteristics["Placement"]["Connection Bias"].value * len(territoryData.connections)

            # Adjust placement score based on preference settings
            if(enemyAdjacentsData):
                # ! Be careful through here, because you cannot assume
                # ! that the best territory found so far is also enemy adjacent
                score += self.characteristics["Preference"]["Aggression"].value
                bestEnemyAdjacentData = self.getTerritoryDataEnemyAdjacent(bestIndex, map) if bestIndex != -1 else []
                bestEnemySize = 0
                bestEnemySize = max([td.army for td in bestEnemyAdjacentData]) if (bestEnemyAdjacentData) else 0
                currEnemySize = max([td.army for td in enemyAdjacentsData])
                # Assume the placement is riskier move if it is more risky to place
                # an army there than the current best placement
                if(currEnemySize > bestEnemySize):
                    score += self.characteristics["Preference"]["Risky"].value
                # Adjust the score if the biggest adjacent enemy army is larger
                # than the biggest adjacent enemy army found so far
                bestEnemyPlayers = set([td.owner for td in bestEnemyAdjacentData]) if (bestEnemyAdjacentData) else set()
                currEnemyPlayers = set([td.owner for td in enemyAdjacentsData])
                bestEnemyPlayerSize = max([len(map.getTerritoriesByPlayer(x))
                                           for x in bestEnemyPlayers]) if bestEnemyPlayers else 0
                currEnemyPlayerSize = max([len(map.getTerritoriesByPlayer(x))
                                           for x in currEnemyPlayers])
                if(currEnemyPlayerSize > bestEnemyPlayerSize):
                    score += self.characteristics["Preference"]["Larger"].value
                if(currEnemyPlayerSize < bestEnemyPlayerSize):
                    score += self.characteristics["Preference"]["Smaller"].value
            else:
                score += self.characteristics["Preference"]["Safe"].value

            # Score multipliers
            # Diminishing Return Multiplier
            diminishingReturnMultiplier = pow(
                self.characteristics["Placement"]["Diminishing Returns"].value, territoryData.army)
            score *= self.characteristics["Placement"]["Diminishing Returns"].value

            if(score > bestScore):
                bestScore = score
                bestIndex = territoryData.index

            print(f"Index: {territoryData.index}, Score: {score}, BestIndex: {bestIndex}")

        return bestIndex

    def placeUnitSetup(self, map):
        emptyTerritoriesIndices = map.getTerritoriesByPlayer("")
        if(emptyTerritoriesIndices):
            territoryIndex = self.pickTerritory(emptyTerritoriesIndices, map)
            map.placeArmy(self.name, 1, territoryIndex)
        else:
            controlledTerritoryIndices = map.getTerritoriesByPlayer(self.name)
            territoryIndex = self.pickTerritory(controlledTerritoryIndices, map)
            map.placeArmy(self.name, 1, territoryIndex)
