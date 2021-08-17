from collections import namedtuple
import math
import random
import copy


AttackSelection = namedtuple('AttackSelection', 'attackIndex defendIndex estimateResult')
MoveSelection = namedtuple('MoveSelection', 'supplyIndex receiveIndex transferAmount')

# TODO: Standardize how to compare the sizes of enemies


class AgentCharacteristic:
    def __init__(self, value, description, adjustmentAmt=1.0):
        self.value = value
        self.description = description
        self.adjustmentAmt = adjustmentAmt

    def __int__(self):
        return self.value

    def __deepcopy__(self):
        cpy = AgentCharacteristic()
        cpy.value = self.value
        cpy.description = self.description
        cpy.adjustmentAmt = self.adjustmentAmt
        return cpy

    def adjust(self):
        self.value += self.adjustmentAmt

    def adjust(self, amt):
        self.value += amt

    def adjust_negative(self):
        self.value -= self.adjustmentAmt

    def adjust_negative(self, amt):
        self.value -= amt

    def adjust_random(self):
        if(bool(random.getrandbits(1))):
            self.adjust()
        else:
            self.adjust_negative()

    def adjust_random(self, amt):
        if(bool(random.getrandbits(1))):
            self.adjust(amt)
        else:
            self.adjust_negative(amt)


class Agent:
    def __init__(self, name):
        self.name = name
        self.characteristics = {
            "Placement": {
                "Anywhere": AgentCharacteristic(3, "Placing a unit anywhere"),
                "Enemy Adjacent": AgentCharacteristic(5, "Placing a unit on a territory connected to a territory controlled by a different player"),
                "Ally Adjacent": AgentCharacteristic(8, "Placing a unit on a territory connected to a territory controlled by the same player"),
                "Border Adjacent": AgentCharacteristic(13, "Placing a unit in a territory that borders a country in a different continent"),
                "Connection Bias": AgentCharacteristic(1, "Placing a unit on a territory with connections to multiple other countries, +value per connection", 0.25),
                "Placement Bias Multiplier": AgentCharacteristic(0.05, "Placing a unit where there already are other units, +value per army", 0.01)
            },
            "Attack": {
                "Anywhere": AgentCharacteristic(3, "Attacking anywhere"),
                "Ally Adjacent": AgentCharacteristic(5, "Attacking a territory connected to another territory controlled by the attacking player"),
                "Border Adjacent": AgentCharacteristic(8, "Attacking a territory on the border of a different continent"),
                "Capture Continent": AgentCharacteristic(13, "Attacking a territory that will give this player control over all territories on a continent if the attack is successful"),
                "Destroy Bias": AgentCharacteristic(1, "Estimated amount of defending units destroyed, +value per unit", 0.1),
                "Remain Bias": AgentCharacteristic(-1, "Estimated amount of attacking units destroyed, -value per unit", 0.1),
                "Safe Threshold": AgentCharacteristic(0.95, "Minimal amount of estimated chance of a successful attack to consider an attack safe, below this amount is considered risky", 0.01),
                "Minimal Success Chance": AgentCharacteristic(0.5, "Minimal amount of estimated chance of successful attack necessary for an attack to be considered viable", 0.01),
                "Minimal Remaining Percent": AgentCharacteristic(0.1, "The amount of units lost before calling off an attack, expressed as a percentage of the amount of units at the start of the attack", 0.01)
            },
            "Movement": {
                "Anywhere": AgentCharacteristic(3, "Moving a unit anywhere"),
                "Enemy Adjacent": AgentCharacteristic(5, "Moving a unit on a territory connected to a territory controlled by a different player"),
                "Ally Adjacent": AgentCharacteristic(8, "Moving a unit on a territory connected to a territory controlled by the same player"),
                "Border Adjacent": AgentCharacteristic(13, "Moving a unit in a territory that borders a country in a different continent"),
                "Bigger Territory": AgentCharacteristic(3, "Moving units onto a territory with more units."),
                "Smaller Territory": AgentCharacteristic(5, "Moving units onto a territory with fewer units."),
                "Connection Bias": AgentCharacteristic(1, "Moving a unit on a territory with connections to multiple other countries, +value per connection", 0.25),
                "Base Transfer Rate": AgentCharacteristic(0.5, "Base percentage of units to transfer should it be necessary", 0.01),
                "Risky Transfer Rate": AgentCharacteristic(0.3, "Percentage of units to transfer if the movement is considered risky", 0.01),
                "Safe Transfer Rate": AgentCharacteristic(0.7, "Percentage of units to transfer if the movement is considered safe", 0.01)
            },
            "Preference": {
                "Larger": AgentCharacteristic(1, "Preference to attack larger players", 0.25),
                "Smaller": AgentCharacteristic(1, "Preference to attack smaller players", 0.25),
                "Aggression": AgentCharacteristic(1, "Preference for aggressive actions", 0.25),
                "Risky": AgentCharacteristic(1, "Preference for risky actions", 0.25),
                "Safe": AgentCharacteristic(1, "Preference for safe actions", 0.25)
            }
        }

    def stats(self):
        output = ""
        for category in self.characteristics.keys():
            output += f"\n{category}:"
            for characteristicName in self.characteristics[category].keys():
                c = self.characteristics[category][characteristicName]
                output += f"\n\t{characteristicName}: {c.value}"
        return output

    def clone(self):
        cpy = Agent(self.name)

        for k in self.characteristics.keys():
            for kk in self.characteristics[k].keys():
                cpy.characteristics[k][kk].value = self.characteristics[k][kk].value

        return cpy

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
        bestScore = -math.inf
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
                # FIXME: Is this really the best way to determine enemy size?
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

            # print(f"Index: {territoryData.index}, Score: {score}, BestIndex: {bestIndex}")

        if(bestIndex == -1):
            raise Exception("No best index for placing a territory")
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

                # Would capturing this territory give a continent bonus?
                unitBonusBeforeCapture = map.getContinentBonus(self.name)
                prevOwner = enemyTerritory.owner
                enemyTerritory.owner = self.name
                unitBonusAfterCapture = map.getContinentBonus(self.name)
                enemyTerritory.owner = prevOwner
                if(unitBonusBeforeCapture != unitBonusAfterCapture):
                    score += self.characteristics["Attack"]["Capture Continent"].value
                    # Consider this an aggressive action
                    score += self.characteristics["Preference"]["Aggression"].value

                # If there is a best value to compare to
                if(bestScore != -1):
                    # FIXME: Is this really the best way to compare enemy size?
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

    def pickTerritoryForMovement(self, map):
        controlledTerritories = map.getTerritoriesByPlayer(self.name)
        controlledTerritoriesThatCanMove = [x for x in controlledTerritories if x.army > 1]

        score = -1
        bestScore = -1
        bestSupplyingTerritory = None
        bestReceivingTerritory = None
        bestTransferAmount = None

        for supplyTerritory in controlledTerritoriesThatCanMove:
            # Get connected territories
            receivableTerritories = [map.territories[index]
                                     for index in supplyTerritory.connections if map.territories[index].owner == self.name]

            for receiveTerritory in receivableTerritories:
                # Skip the movement calculation process if attempting to move units to self
                if(supplyTerritory == receiveTerritory):
                    continue

                score = 0
                # Calculate movement score based on movement settings
                score += self.characteristics["Movement"]["Anywhere"].value
                score += self.characteristics["Movement"]["Enemy Adjacent"].value if self.getTerritoryDataEnemyAdjacent(
                    receiveTerritory.index, map) else 0
                score += self.characteristics["Movement"]["Ally Adjacent"].value if self.getTerritoryDataAllyAdjacent(
                    receiveTerritory.index, map) else 0
                score += self.characteristics["Movement"]["Border Adjacent"].value if self.getTerritoryDataBorderAdjacent(
                    receiveTerritory.index, map) else 0
                score += self.characteristics["Movement"]["Connection Bias"].value * len(receiveTerritory.connections)
                score += self.characteristics["Movement"]["Bigger Territory"].value if receiveTerritory.army > supplyTerritory.army else 0
                score += self.characteristics["Movement"]["Smaller Territory"].value if receiveTerritory.army < supplyTerritory.army else 0

                # Calculate movement score based on preference settings
                # Consider it to be aggressive to move into a territory with more enemy than ally connections
                isAggressive = len(self.getTerritoryDataEnemyAdjacent(receiveTerritory.index, map)) > len(
                    self.getTerritoryDataAllyAdjacent(receiveTerritory.index, map))
                score += self.characteristics["Preference"]["Aggression"].value if isAggressive else 0
                # Consider it risky to move units away from a territory with enemy connections
                isRisky = len(self.getTerritoryDataEnemyAdjacent(supplyTerritory.index, map)) > 0
                score += self.characteristics["Preference"]["Risky"].value if isRisky else 0
                # Consider it safe to move units away from a territory without enemy connections
                isSafe = len(self.getTerritoryDataEnemyAdjacent(supplyTerritory.index, map)) == 0
                score += self.characteristics["Preference"]["Safe"].value if isSafe else 0

                # Consider preference to move towards smaller/bigger players as a prescursor to attack
                # ! Be careful here, because you cannot assume the following:
                # ! 1.) The current best movement receiver is connected to an enemy territory
                # ! 2.) The current receiver is connected to an enemy territory
                # ! 3.) That any territory is connected to a single enemy

                # FIXME: Is this the best way to compare enemy size?

                currTotalEnemySize = 0
                try:
                    currEnemyData = self.getTerritoryDataEnemyAdjacent(receiveTerritory.index, map)
                    currConnectedEnemyNames = [x.owner for x in currEnemyData]
                    # FIXME: Is this the best way to compare enemy size?
                    currConnectedEnemySize = [map.getTotalArmiesByPlayer(x) for x in currConnectedEnemyNames]
                    currTotalEnemySize = max(currConnectedEnemySize)
                except:
                    pass

                currBestTotalEnemySize = 0
                try:
                    currBestEnemyData = self.getTerritoryDataEnemyAdjacent(bestReceivingTerritory.index, map)
                    currBestConnectedEnemyNames = [x.owner for x in currBestEnemyData]

                    currBestConnectedEnemySize = [map.getTotalArmiesByPlayer(x) for x in currBestConnectedEnemyNames]
                    currBestTotalEnemySize = max(currBestConnectedEnemySize)
                except:
                    pass

                if(currTotalEnemySize > currBestTotalEnemySize):
                    score += self.characteristics["Preference"]["Larger"].value
                if(currTotalEnemySize < currBestTotalEnemySize):
                    score += self.characteristics["Preference"]["Smaller"].value

                # Determine if this is the best movement
                if(score > bestScore):
                    # Determine how many armies to transfer over
                    percentToTransfer = self.characteristics["Movement"]["Base Transfer Rate"].value
                    if(isRisky):
                        percentToTransfer = self.characteristics["Movement"]["Risky Transfer Rate"].value
                    if(isSafe):
                        percentToTransfer = self.characteristics["Movement"]["Safe Transfer Rate"].value

                    unitsToTransfer = math.floor(supplyTerritory.army * percentToTransfer)
                    # Don't move all units, at least 1 must stay on the supplying territory
                    if(supplyTerritory.army - unitsToTransfer <= 0):
                        unitsToTransfer = supplyTerritory.army - 1

                    # Set best stats
                    bestScore = score
                    bestSupplyingTerritory = supplyTerritory
                    bestReceivingTerritory = receiveTerritory
                    bestTransferAmount = unitsToTransfer

        # ! Don't assume that the agent CAN move an army

        if(bestScore == -1):
            return None
        else:
            return MoveSelection(bestSupplyingTerritory.index, bestReceivingTerritory.index, bestTransferAmount)

    def attackTerritory(self, pickTerritoryResult, map, atkSys):
        if(not pickTerritoryResult):
            # rm print(f"{self.name} chose not to attack this turn")
            return None

        attackingTerritory = map.territories[pickTerritoryResult.attackIndex]
        defendingTerritory = map.territories[pickTerritoryResult.defendIndex]

        attackingArmies = attackingTerritory.army - 1  # Keep one remaining on the territory
        defendingArmies = defendingTerritory.army

        minimumAmountRemaining = math.floor(
            attackingArmies * self.characteristics["Attack"]["Minimal Remaining Percent"].value)

        # Actually perform the attack
        attackResult = atkSys.attack(attackingArmies, defendingArmies, minimumAmountRemaining)

        # rm print(f"Attacking ({defendingTerritory}) from ({attackingTerritory}) was {'successful' if (attackResult.defenders == 0) else 'unsuccessful'}")

        # FIXME: Shouldn't this really be handled by the map object, not the agent?
        # Keep any remaining armies
        # Don't forget about the 1 that wasn't allowed to leave
        attackingTerritory.army = attackResult.attackers + 1

        # Let the defenders keep their remaining armies
        defendingTerritory.army = attackResult.defenders

        # If the attack was successful, change ownership
        attackSuccessful = (attackResult.defenders == 0)
        if(attackSuccessful):
            defendingTerritory.owner = self.name
            # Take an attacking army and place it on the new territory
            defendingTerritory.army = 1
            attackingTerritory.army -= 1

        return attackResult

    def placeUnit(self, map):
        controlledTerritoryIndices = map.getTerritoriesByPlayer(self.name)
        territoryIndex = self.pickTerritoryForPlacement(controlledTerritoryIndices, map)
        map.placeArmy(self.name, 1, territoryIndex)
        return territoryIndex

    def placeUnitSetup(self, map):
        emptyTerritoriesIndices = map.getTerritoriesByPlayer("")
        if(emptyTerritoriesIndices):
            territoryIndex = self.pickTerritoryForPlacement(emptyTerritoriesIndices, map)
            map.placeArmy(self.name, 1, territoryIndex)
        else:
            self.placeUnit(map)

    def mutate(self, recursiveChance=0.8, majorMutationChance=0.6, mutationMultiplier=1.0):

        recurse = True
        while(recurse):
            # Determine if recursion is necessary
            recurse = random.random() < recursiveChance
            recursiveChance = recursiveChance/2

            # Determine what to mutate
            characteristicGroupName = random.choice(list(self.characteristics.keys()))
            # Determine how to mutate (Single attribute vs. entire group)
            isMajorMutation = random.random() < majorMutationChance
            # Perform mutation
            self.mutateCharacteristic(characteristicGroupName, isMajorMutation, mutationMultiplier)

    def mutateCharacteristic(self, characteristicGroupName, isMajorMutation=False, mutationMultiplier=1.0):
        if(isMajorMutation):
            for characteristic in self.characteristics[characteristicGroupName].values():
                characteristic.adjust_random(characteristic.adjustmentAmt * mutationMultiplier)
        else:
            randomCharacteristic = random.choice(list(self.characteristics[characteristicGroupName].values()))
            randomCharacteristic.adjust_random(randomCharacteristic.adjustmentAmt * mutationMultiplier)
