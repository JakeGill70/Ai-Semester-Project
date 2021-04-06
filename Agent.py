from collections import namedtuple


AttackSelection = namedtuple('AttackSelection', 'attackIndex defendIndex estimateResult')


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
                "Enemy Adjacent": AgentCharacteristic(5, "Placing a unit on a territory connected to a territory controlled by a different player"),
                "Ally Adjacent": AgentCharacteristic(8, "Placing a unit on a territory connected to a territory controlled by the same player"),
                "Border Adjacent": AgentCharacteristic(13, "Placing a unit in a territory that borders a country in a different continent"),
                "Connection Bias": AgentCharacteristic(1, "Placing a unit on a territory with connections to multiple other countries, +value per connection"),
                "Placement Bias Multiplier": AgentCharacteristic(0.5, "Placing a unit where there already are other units, *value per army")
            },
            "Attack": {
                "Anywhere": AgentCharacteristic(3, "Attacking anywhere"),
                "Ally Adjacent": AgentCharacteristic(5, "Attacking a territory connected to another territory controlled by the attacking player"),
                "Border Adjacent": AgentCharacteristic(8, "Attacking a territory on the border of a different continent"),
                "Destroy Bias": AgentCharacteristic(1, "Estimated amount of defending units destroyed, +1 value per unit"),
                "Remain Bias": AgentCharacteristic(-1, "Estimated amount of attacking units destroyed, -1 value per unit"),
                "Safe Threshold": AgentCharacteristic(0.95, "Minimal amount of estimated chance of a successful attack to consider an attack safe, below this amount is considered risky"),
                "Minimal Success Chance": AgentCharacteristic(0.5, "Minimal amount of estimated chance of successful attack necessary for an attack to be considered viable")
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

    def getTerritoryDataAllyAdjacent(self, territoryIndex, map):
        territoryData = map.territories[territoryIndex]
        adjacentTerritoryData = [map.territories[ti] for ti in territoryData.connections
                                 if map.territories[ti].owner == self.name]
        return adjacentTerritoryData

    def pickTerritoryForPlacement(self, possibleTerritoryData, map):
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
            score += self.characteristics["Placement"]["Ally Adjacent"].value if self.getTerritoryDataAllyAdjacent(
                territoryData.index, map) else 0
            score += self.characteristics["Placement"]["Border Adjacent"].value if self.getTerritoryDataBorderAdjacent(
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
                self.characteristics["Placement"]["Placement Bias Multiplier"].value, territoryData.army)
            score *= diminishingReturnMultiplier

            if(score > bestScore):
                bestScore = score
                bestIndex = territoryData.index

            #print(f"Index: {territoryData.index}, Score: {score}, BestIndex: {bestIndex}")

        return bestIndex

    def pickTerritoryForAttack(self, map, atkSys):
        controlledTerritories = map.getTerritoriesByPlayer(self.name)
        controlledTerritoriesThatCanAttack = [x for x in controlledTerritories if x.army > 1]

        score = -1
        bestScore = -1
        bestAttackingTerritory = None
        bestDefendingTerritory = None
        bestAttackEstimate = None
        for territory in controlledTerritoriesThatCanAttack:
            enemyConnections = [map.territories[index]
                                for index in territory.connections if map.territories[index].owner != self.name]
            for enemyTerritory in enemyConnections:
                # Get attack estimate
                attackEstimate = atkSys.getAttackEstimate(territory.army, enemyTerritory.army)

                # Determine if the attack is viable
                if(attackEstimate.attackSuccessChance < self.characteristics["Attack"]["Minimal Success Chance"].value):
                    # Don't bother calculating the score from this point onward
                    # rm print(f"Attacking ({enemyTerritory}) from ({territory}) is a non-viable strategy with only a {attackEstimate.attackSuccessChance * 100}% chance of success")
                    continue

                score = 0
                score += self.characteristics["Attack"]["Anywhere"].value
                score += self.characteristics["Attack"]["Ally Adjacent"].value if self.getTerritoryDataEnemyAdjacent(
                    territory.index, map) else 0
                score += self.characteristics["Attack"]["Border Adjacent"].value if self.getTerritoryDataBorderAdjacent(
                    enemyTerritory.index, map) else 0

                score += self.characteristics["Attack"]["Remain Bias"].value * \
                    (territory.army - attackEstimate.attackers)
                score += self.characteristics["Attack"]["Destroy Bias"].value * \
                    (enemyTerritory.army - attackEstimate.defenders)

                score += self.characteristics["Preference"]["Risky"].value if \
                    attackEstimate.attackSuccessChance < self.characteristics["Attack"]["Safe Threshold"].value else 0
                score += self.characteristics["Preference"]["Safe"].value if  \
                    attackEstimate.attackSuccessChance >= self.characteristics["Attack"]["Safe Threshold"].value else 0

                # If there is a best value to compare to
                if(bestScore != -1):
                    currEnemySize = len(map.getTerritoriesByPlayer(enemyTerritory.owner))
                    bestEnemySize = len(map.getTerritoriesByPlayer(bestDefendingTerritory.owner))
                    if(currEnemySize > bestEnemySize):
                        score += self.characteristics["Preference"]["Larger"].value
                    if(currEnemySize < bestEnemySize):
                        score += self.characteristics["Preference"]["Smaller"].value

                if(score > bestScore):
                    bestScore = score
                    bestAttackingTerritory = territory
                    bestDefendingTerritory = enemyTerritory
                    bestAttackEstimate = attackEstimate

                # rm print(f"Attacking ({enemyTerritory}) from ({territory}) scored {score}, and has a {attackEstimate.attackSuccessChance * 100}% chance of success. Best Score: {bestScore}")

        # Return 'None' if there are no viable attack options
        if(bestScore == -1):
            return None

        # Return the best option found
        return AttackSelection(bestAttackingTerritory.index, bestDefendingTerritory.index, bestAttackEstimate)

    def placeUnit(self, map):
        controlledTerritoryIndices = map.getTerritoriesByPlayer(self.name)
        territoryIndex = self.pickTerritoryForPlacement(controlledTerritoryIndices, map)
        map.placeArmy(self.name, 1, territoryIndex)

    def placeUnitSetup(self, map):
        emptyTerritoriesIndices = map.getTerritoriesByPlayer("")
        if(emptyTerritoriesIndices):
            territoryIndex = self.pickTerritoryForPlacement(emptyTerritoriesIndices, map)
            map.placeArmy(self.name, 1, territoryIndex)
        else:
            self.placeUnit(map)
