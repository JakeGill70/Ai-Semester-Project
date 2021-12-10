from collections import namedtuple
import math
import random
import copy
import json
from itertools import combinations_with_replacement, permutations
import hashlib

AttackSelection = namedtuple('AttackSelection',
                             'attackIndex defendIndex estimateResult')
AttackSelectionMaxn = namedtuple(
    'AttackSelection', 'attackIndex defendIndex estimateResult mapScore')
MoveSelection = namedtuple('MoveSelection',
                           'supplyIndex receiveIndex transferAmount')


class AgentCharacteristic:
    def __init__(self,
                 value,
                 description,
                 adjustmentAmt=1.0,
                 lowerLimit=-math.inf,
                 upperLimit=math.inf):
        self.value = value
        self.description = description
        self.adjustmentAmt = adjustmentAmt
        self.lowerLimit = lowerLimit
        self.upperLimit = upperLimit

    def __int__(self):
        return self.value

    def __deepcopy__(self):
        cpy = AgentCharacteristic()
        cpy.value = self.value
        cpy.description = self.description
        cpy.adjustmentAmt = self.adjustmentAmt
        return cpy

    def toJSON(self):
        return f"{{\"value\" : {self.value}, \"adjustmentAmount\" : {self.adjustmentAmt}, \"lowerLimit\" : {self.lowerLimit}, \"upperLimit\" : {self.upperLimit}, \"description\" : \"{self.description}\"}}"

    def adjust(self):
        self.adjust(self.adjustmentAmt)

    def adjust(self, amt):
        self.value += amt
        if (self.value > self.upperLimit):
            self.value = self.upperLimit
        elif (self.value < self.lowerLimit):
            self.value = self.lowerLimit

    def adjust_negative(self):
        self.adjust(-self.adjustmentAmt)

    def adjust_negative(self, amt):
        self.adjust(-amt)

    def adjust_random(self):
        if (bool(random.getrandbits(1))):
            self.adjust()
        else:
            self.adjust_negative()

    def adjust_random(self, amt):
        if (bool(random.getrandbits(1))):
            self.adjust(amt)
        else:
            self.adjust_negative(amt)


class Agent:
    def __init__(self, name="Unnamed Agent"):
        self.name = name
        self.bestMovementCache = {}
        self.allValidAttackOrdersCache = {}
        self.scoreGameStateCache = {}
        self.characteristics = {
            "Placement": {
                "Anywhere":AgentCharacteristic(0, "Placing a unit anywhere"),
                "Enemy Adjacent":AgentCharacteristic(0,"Placing a unit on a territory connected to a territory controlled by a different player"),
                "Ally Adjacent":AgentCharacteristic(0, "Placing a unit on a territory connected to a territory controlled by the same player"),
                "Border Adjacent":AgentCharacteristic(0,"Placing a unit in a territory that borders a country in a different continent"),
                "Connection Bias":AgentCharacteristic(0, "Placing a unit on a territory with connections to multiple other countries, +value per connection",0.25),
                "Placement Bias Multiplier":AgentCharacteristic(0.75,"Placing a unit where there already are other units, value^(armies on territory)", 0.05,lowerLimit=0,upperLimit=1)
            },
            "Attack": {
                "Anywhere":AgentCharacteristic(0, "Attacking anywhere"),
                "Ally Adjacent":AgentCharacteristic(0,"Attacking a territory connected to another territory controlled by the attacking player"),
                "Border Adjacent":AgentCharacteristic(0,"Attacking a territory on the border of a different continent"),
                "Capture Continent":AgentCharacteristic(0, "Attacking a territory that will give this player control over all territories on a continent if the attack is successful"),
                "Destroy Bias":AgentCharacteristic(0,"Estimated amount of defending units destroyed, +value per unit",0.1),
                "Remain Bias":AgentCharacteristic(0,"Estimated amount of attacking units destroyed, -value per unit", 0.1),
                "Safe Threshold":AgentCharacteristic(0.95,"Minimal amount of estimated chance of a successful attack to consider an attack safe, below this amount is considered risky",0.05,lowerLimit=0,upperLimit=1),
                "Minimal Success Chance":AgentCharacteristic(0.5,"Minimal amount of estimated chance of successful attack necessary for an attack to be considered viable",0.05,lowerLimit=0,upperLimit=1),
                "Minimal Remaining Percent":AgentCharacteristic(0.1,"The amount of units lost before calling off an attack, expressed as a percentage of the amount of units at the start of the attack",0.05,lowerLimit=0,upperLimit=1)
            },
            "Movement": {
                "Anywhere":AgentCharacteristic(0, "Moving a unit anywhere"),
                "Enemy Adjacent":AgentCharacteristic(0,"Moving a unit on a territory connected to a territory controlled by a different player"),
                "Ally Adjacent":AgentCharacteristic(0, "Moving a unit on a territory connected to a territory controlled by the same player"),
                "Border Adjacent":AgentCharacteristic(0,"Moving a unit in a territory that borders a country in a different continent"),
                "Bigger Territory":AgentCharacteristic(0, "Moving units onto a territory with more units."),
                "Smaller Territory":AgentCharacteristic(0, "Moving units onto a territory with fewer units."),
                "Connection Bias":AgentCharacteristic(0,"Moving a unit on a territory with connections to multiple other countries, +value per connection",0.25),
                "Base Transfer Rate":AgentCharacteristic(0.5,"Base percentage of units to transfer should it be necessary", 0.05),
                "Risky Transfer Rate":AgentCharacteristic(0.25,"Percentage of units to transfer if the movement is considered risky", 0.05),
                "Safe Transfer Rate":AgentCharacteristic(0.75,"Percentage of units to transfer if the movement is considered safe",0.05)
            },
            "Preference": {
                "Larger":AgentCharacteristic(1, "Preference to attack larger players",0.25),
                "Smaller":AgentCharacteristic(1, "Preference to attack smaller players", 0.25),
                "Risky":AgentCharacteristic(1, "Preference for risky actions", 0.25),
                "Safe":AgentCharacteristic(1, "Preference for safe actions", 0.25)
            },
            "Consideration": {
                "Armies":AgentCharacteristic(0, "Owning an army, +value each"),
                "Territories":AgentCharacteristic(0, "Owning a territory, +value each"),
                "Armies Enemy Adjacent":AgentCharacteristic(0,"Owning an army next to an enemy controlled territory, +value each"),
                "Territories Enemy Adjacent":AgentCharacteristic(0,"Owning a territory with an enemy connection, +value for each connection"),
                "Army Upkeep":AgentCharacteristic(0,"Armies given to player at start of next turn, +value for each"),
                "Continents":AgentCharacteristic(0, "Owning a continent, +value each", 5),
                "Remaining Players":AgentCharacteristic(0,"Number of remaining players on the game board, +value for each", 5),
                # Consider continents, territories, armies, and adjacent armies controlled by other players
                "Enemy Armies Adjacent":AgentCharacteristic(0,"Armies controlled by other players adjacent to player controlled territories, +value each"),
                "Enemy Territories Adjacent":AgentCharacteristic(0, "Territories controlled by other players adjacent to player controlled territories, +value each")
            }
        }

    def toJSON(self):
        s = f"{{\"name\": \"{self.name}\", \"characteristics\": {{ "
        for groupKey, groupDict in self.characteristics.items():
            s += f"\"{groupKey}\" : {{"
            for characteristicName, characteristicObject in groupDict.items():
                s += (
                    f"\"{characteristicName}\" : {characteristicObject.toJSON()},"
                )
            s = s[:-1]
            s += "},"
        s = s[:-1]
        s += "} }"
        return s

    def getHash(self):
        return hashlib.md5(self.toJSON().encode()).hexdigest()

    def getHash_ConsiderationOnly(self):
        considerationValuesAsText = "|".join(str(c.value) for c in self.characteristics["Consideration"].values())
        return hashlib.md5(considerationValuesAsText.encode()).hexdigest()

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
                cpy.characteristics[k][kk].value = self.characteristics[k][
                    kk].value

        return cpy

    def getTerritoryDataBorderAdjacent(self, territoryIndex, map):
        territoryData = map.territories[territoryIndex]
        adjacentTerritoryData = [map.territories[ti] for ti in territoryData.connections if map.territories[ti].continent != territoryData.continent]
        return adjacentTerritoryData

    def getTerritoryDataEnemyAdjacent(self, territoryIndex, map):
        territoryData = map.territories[territoryIndex]
        adjacentTerritoryData = [map.territories[ti] for ti in territoryData.connections if map.territories[ti].owner != self.name and map.territories[ti].owner != "" ]
        return adjacentTerritoryData

    def getTerritoryDataAllyAdjacent(self, territoryIndex, map):
        territoryData = map.territories[territoryIndex]
        adjacentTerritoryData = [map.territories[ti] for ti in territoryData.connections if map.territories[ti].owner == self.name]
        return adjacentTerritoryData

    def pickTerritoryForPlacement(self, possibleTerritoryData, map):
        if(len(possibleTerritoryData) == 0):
            # If there was no valid territory data given, just grab everything
            possibleTerritoryData = map.getTerritoriesByPlayer(self.name)
        if(len(possibleTerritoryData) == 0):
            # If there is still no valid data, then this agent is dead and something has gone wrong,
            # so just return a None and let the caller deal with it.
            return None
        score = 0
        bestScore = -math.inf
        bestIndex = random.choice(possibleTerritoryData).index
        for territoryData in possibleTerritoryData:
            score = 0
            # Calculate placement score based on placement settings
            score += self.characteristics["Placement"]["Anywhere"].value
            score += self.characteristics["Placement"]["Enemy Adjacent"].value if self.getTerritoryDataEnemyAdjacent(territoryData.index, map) else 0
            score += self.characteristics["Placement"]["Ally Adjacent"].value if self.getTerritoryDataAllyAdjacent(territoryData.index, map) else 0
            score += self.characteristics["Placement"]["Border Adjacent"].value if self.getTerritoryDataBorderAdjacent(territoryData.index, map) else 0
            score += self.characteristics["Placement"]["Connection Bias"].value * len(territoryData.connections)

            # Adjust placement score based on preference settings
            enemyAdjacentsData = self.getTerritoryDataEnemyAdjacent(territoryData.index, map)
            if (enemyAdjacentsData):
                # ! Be careful through here, because you cannot assume
                # ! that the best territory found so far is also enemy adjacent
                bestEnemyAdjacentData = self.getTerritoryDataEnemyAdjacent(bestIndex, map) if bestIndex != -1 else []
                bestEnemySize = 0
                # FIXME: Is this really the best way to determine enemy size?
                bestEnemySize = max([td.getArmy() for td in bestEnemyAdjacentData]) if (bestEnemyAdjacentData) else 0
                currEnemySize = max([td.getArmy() for td in enemyAdjacentsData])
                # Assume the placement is riskier move if it is more risky to place
                # an army there than the current best placement
                if (currEnemySize > bestEnemySize):
                    score += self.characteristics["Preference"]["Risky"].value
                # Adjust the score if the biggest adjacent enemy army is larger
                # than the biggest adjacent enemy army found so far
                bestEnemyPlayers = set([td.owner for td in bestEnemyAdjacentData]) if (bestEnemyAdjacentData) else set()
                currEnemyPlayers = set([td.owner for td in enemyAdjacentsData])
                bestEnemyPlayerSize = max([len(map.getTerritoriesByPlayer(x)) for x in bestEnemyPlayers]) if bestEnemyPlayers else 0
                currEnemyPlayerSize = max([len(map.getTerritoriesByPlayer(x)) for x in currEnemyPlayers])
                if (currEnemyPlayerSize > bestEnemyPlayerSize):
                    score += self.characteristics["Preference"]["Larger"].value
                if (currEnemyPlayerSize < bestEnemyPlayerSize):
                    score += self.characteristics["Preference"]["Smaller"].value
            else:
                score += self.characteristics["Preference"]["Safe"].value

            # Score multipliers
            # Diminishing Return Multiplier
            diminishingReturnMultiplier = pow(self.characteristics["Placement"]["Placement Bias Multiplier"].value, territoryData.getArmy())
            score *= diminishingReturnMultiplier

            if (score > bestScore):
                bestScore = score
                bestIndex = territoryData.index

        return bestIndex

    def pickTerritoryForAttack(self, map, atkSys):
        controlledTerritories = map.getTerritoriesByPlayer(self.name)
        controlledTerritoriesThatCanAttack = [t for t in controlledTerritories if t.getArmy() > 1]

        score = -1
        bestScore = -1
        bestAttackingTerritory = None
        bestDefendingTerritory = None
        bestAttackEstimate = None
        for territory in controlledTerritoriesThatCanAttack:
            enemyConnections = [map.territories[index] for index in territory.connections if map.territories[index].owner != self.name]

            for enemyTerritory in enemyConnections:
                # Get attack estimate
                attackEstimate = atkSys.getAttackEstimate(territory.getArmy(), enemyTerritory.getArmy())

                # Determine if the attack is viable
                if (attackEstimate.attackSuccessChance < self.characteristics["Attack"]["Minimal Success Chance"].value):
                    # Don't bother calculating the score from this point onward
                    # rm print(f"Attacking ({enemyTerritory}) from ({territory}) is a non-viable strategy with only a {attackEstimate.attackSuccessChance * 100}% chance of success")
                    continue

                score = 0
                score += self.characteristics["Attack"]["Anywhere"].value
                score += self.characteristics["Attack"]["Ally Adjacent"].value if self.getTerritoryDataEnemyAdjacent(territory.index, map) else 0
                score += self.characteristics["Attack"]["Border Adjacent"].value if self.getTerritoryDataBorderAdjacent(enemyTerritory.index, map) else 0

                score += self.characteristics["Attack"]["Remain Bias"].value * (territory.getArmy() - attackEstimate.attackers)
                score += self.characteristics["Attack"]["Destroy Bias"].value * (enemyTerritory.getArmy() - attackEstimate.defenders)

                score += self.characteristics["Preference"]["Risky"].value if attackEstimate.attackSuccessChance < self.characteristics["Attack"]["Safe Threshold"].value else 0
                score += self.characteristics["Preference"]["Safe"].value if attackEstimate.attackSuccessChance >= self.characteristics["Attack"]["Safe Threshold"].value else 0

                # Would capturing this territory give a continent bonus?
                unitBonusBeforeCapture = map.getContinentBonus(self.name)
                prevOwner = enemyTerritory.owner
                enemyTerritory.owner = self.name
                unitBonusAfterCapture = map.getContinentBonus(self.name)
                enemyTerritory.owner = prevOwner
                if (unitBonusBeforeCapture != unitBonusAfterCapture):
                    score += self.characteristics["Attack"]["Capture Continent"].value

                # If there is a best value to compare to
                if (bestScore != -1):
                    currEnemySize = map.getPlayerSize(enemyTerritory.owner)
                    bestEnemySize = map.getPlayerSize(bestDefendingTerritory.owner)
                    if (currEnemySize > bestEnemySize):
                        score += self.characteristics["Preference"]["Larger"].value
                    if (currEnemySize < bestEnemySize):
                        score += self.characteristics["Preference"]["Smaller"].value

                if (score > bestScore):
                    bestScore = score
                    bestAttackingTerritory = territory
                    bestDefendingTerritory = enemyTerritory
                    bestAttackEstimate = attackEstimate

                # rm print(f"Attacking ({enemyTerritory}) from ({territory}) scored {score}, and has a {attackEstimate.attackSuccessChance * 100}% chance of success. Best Score: {bestScore}")

        # Return 'None' if there are no viable attack options
        if (bestScore == -1):
            return None

        # Return the best option found
        return AttackSelection(bestAttackingTerritory.index, bestDefendingTerritory.index, bestAttackEstimate)

    def pickTerritoryForMovement(self, map):
        controlledTerritories = map.getTerritoriesByPlayer(self.name)
        controlledTerritoriesThatCanMove = [t for t in controlledTerritories if t.getArmy() > 1]

        score = -1
        bestScore = -1
        bestSupplyingTerritory = None
        bestReceivingTerritory = None
        bestTransferAmount = None

        for supplyTerritory in controlledTerritoriesThatCanMove:
            # Get connected territories
            receivableTerritories = [
                map.territories[index] for index in supplyTerritory.connections
                if map.territories[index].owner == self.name
            ]

            for receiveTerritory in receivableTerritories:
                # Skip the movement calculation process if attempting to move units to self
                if (supplyTerritory == receiveTerritory):
                    continue

                score = 0
                # Calculate movement score based on movement settings
                score += self.characteristics["Movement"]["Anywhere"].value
                score += self.characteristics["Movement"]["Enemy Adjacent"].value if self.getTerritoryDataEnemyAdjacent(receiveTerritory.index, map) else 0
                score += self.characteristics["Movement"]["Ally Adjacent"].value if self.getTerritoryDataAllyAdjacent(receiveTerritory.index, map) else 0
                score += self.characteristics["Movement"]["Border Adjacent"].value if self.getTerritoryDataBorderAdjacent(receiveTerritory.index, map) else 0
                score += self.characteristics["Movement"]["Connection Bias"].value * len(receiveTerritory.connections)
                score += self.characteristics["Movement"]["Bigger Territory"].value if receiveTerritory.getArmy() > supplyTerritory.getArmy() else 0
                score += self.characteristics["Movement"]["Smaller Territory"].value if receiveTerritory.getArmy() < supplyTerritory.getArmy() else 0

                # Calculate movement score based on preference settings
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
                # TODO: Add more comments and simplify this logic - it smells bad!

                currTotalEnemySize = 0
                try:
                    currEnemyData = self.getTerritoryDataEnemyAdjacent(receiveTerritory.index, map)
                    currConnectedEnemyNames = [x.owner for x in currEnemyData]
                    # FIXME: Is this the best way to compare enemy size?
                    currConnectedEnemySize = [map.getPlayerSize(x) for x in currConnectedEnemyNames]
                    currTotalEnemySize = sum(currConnectedEnemySize)
                except:
                    pass

                currBestTotalEnemySize = 0
                try:
                    currBestEnemyData = self.getTerritoryDataEnemyAdjacent(bestReceivingTerritory.index, map)
                    currBestConnectedEnemyNames = [x.owner for x in currBestEnemyData]

                    currBestConnectedEnemySize = [map.getPlayerSize(x) for x in currBestConnectedEnemyNames]
                    currBestTotalEnemySize = sum(currBestConnectedEnemySize)
                except:
                    pass

                if (currTotalEnemySize > currBestTotalEnemySize):
                    score += self.characteristics["Preference"]["Larger"].value
                if (currTotalEnemySize < currBestTotalEnemySize):
                    score += self.characteristics["Preference"]["Smaller"].value

                # Determine if this is the best movement
                if (score > bestScore):
                    # Determine how many armies to transfer over
                    percentToTransfer = self.characteristics["Movement"]["Base Transfer Rate"].value
                    if (isRisky):
                        percentToTransfer = self.characteristics["Movement"]["Risky Transfer Rate"].value
                    if (isSafe):
                        percentToTransfer = self.characteristics["Movement"]["Safe Transfer Rate"].value

                    # Clamp percent to transfer to be a percentage value
                    percentToTransfer = max(0, min(percentToTransfer, 1))

                    unitsToTransfer = math.floor(supplyTerritory.getArmy() * percentToTransfer)
                    # Don't move all units, at least 1 must stay on the supplying territory
                    # Remember that a territory must have at least 2 units to perform a transfer:
                    #       1 unit to remain on the territory, and the 1 unit to transfer
                    if (supplyTerritory.getArmy() - unitsToTransfer < 2):
                        unitsToTransfer = supplyTerritory.getArmy() - 1

                    if (unitsToTransfer > 0):
                        # Don't consider it a best movement if no units actually get moved
                        # Set best stats
                        bestScore = score
                        bestSupplyingTerritory = supplyTerritory
                        bestReceivingTerritory = receiveTerritory
                        bestTransferAmount = unitsToTransfer

        # ! Don't assume that the agent CAN move an army

        if (bestScore == -1):
            return None
        else:
            return MoveSelection(bestSupplyingTerritory.index, bestReceivingTerritory.index, bestTransferAmount)

    def attackTerritory(self, pickTerritoryResult, map, atkSys):
        return self.attackTerritory(pickTerritoryResult.attackIndex, pickTerritoryResult.defendIndex, map, atkSys)

    def attackTerritory(self, attackIndex, defendIndex, map, atkSys):
        if (attackIndex == None or defendIndex == None):
            # rm print(f"{self.name} chose not to attack this turn")
            return None

        attackingTerritory = map.territories[attackIndex]
        defendingTerritory = map.territories[defendIndex]

        attackingArmies = attackingTerritory.getArmy() - 1  # Keep one remaining on the territory
        defendingArmies = defendingTerritory.getArmy()

        minimumAmountRemaining = math.floor(attackingArmies * self.characteristics["Attack"]["Minimal Remaining Percent"].value)

        # Actually perform the attack
        attackResult = atkSys.attack(attackingArmies, defendingArmies, minimumAmountRemaining)

        # rm print(f"Attacking ({defendingTerritory}) from ({attackingTerritory}) was {'successful' if (attackResult.defenders == 0) else 'unsuccessful'}")

        # FIXME: Shouldn't this really be handled by the map object, not the agent?

        # If the attack was successful, change ownership
        attackSuccessful = (attackResult.defenders == 0)
        if (attackSuccessful):
            defendingTerritory.owner = self.name

            # Keep any remaining armies
            attackingTerritory.setArmy(attackResult.attackers)
            # Take an attacking army and place it on the new territory
            defendingTerritory.setArmy(1)
        else:
            # Keep any remaining armies
            # Don't forget about the 1 that wasn't allowed to leave
            attackingTerritory.setArmy(attackResult.attackers + 1)
            # Let the defenders keep their remaining armies
            defendingTerritory.setArmy(attackResult.defenders)
        return attackResult


    def placeUnit(self, map):
        controlledTerritoryIndices = map.getTerritoriesByPlayer(self.name)
        territoryIndex = self.pickTerritoryForPlacement(controlledTerritoryIndices, map)
        if(territoryIndex):
            map.placeArmy(self.name, 1, territoryIndex)
        return territoryIndex

    def placeUnitSetup(self, map):
        emptyTerritoriesIndices = map.getTerritoriesByPlayer("")
        if (emptyTerritoriesIndices):
            territoryIndex = self.pickTerritoryForPlacement(emptyTerritoriesIndices, map)
            map.placeArmy(self.name, 1, territoryIndex)
        else:
            self.placeUnit(map)

    def mutate(self, recursiveChance=0.8, majorMutationChance=0.6, mutationMultiplier=1.0):

        recurse = True
        while (recurse):
            # Determine if recursion is necessary
            recurse = random.random() < recursiveChance
            recursiveChance = recursiveChance / 2

            # Determine what to mutate
            characteristicGroupName = random.choice(
                list(self.characteristics.keys()))
            # Determine how to mutate (Single attribute vs. entire group)
            isMajorMutation = random.random() < majorMutationChance
            # Perform mutation
            self.mutateCharacteristic(characteristicGroupName, isMajorMutation, mutationMultiplier)

    def mutateCharacteristic(self, characteristicGroupName, isMajorMutation=False, mutationMultiplier=1.0):
        if (isMajorMutation):
            for characteristic in self.characteristics[characteristicGroupName].values():
                characteristic.adjust_random(characteristic.adjustmentAmt * mutationMultiplier)
        else:
            randomCharacteristic = random.choice(list(self.characteristics[characteristicGroupName].values()))
            randomCharacteristic.adjust_random(randomCharacteristic.adjustmentAmt * mutationMultiplier)

    #####################################################
    #                                                   #
    #                   Max^n Methods                   #
    #                                                   #
    #####################################################

    def convertArmiesToPlaceToGroupSize(self, armiesToPlace):
        groupSize = -1
        if (armiesToPlace <= 10):
            groupSize = armiesToPlace
        else:
            armyGroupSize = math.ceil(armiesToPlace * 0.1)
            groupSize = math.ceil((armiesToPlace) / armyGroupSize)
        return groupSize

    def getTerritoryIndicesEligableForPlacement(self, map):
        controlledTerritoryIndices = [t.index for t in map.getTerritoriesByPlayer(self.name)]
        eligableTerritoryIndices = set()
        for tid in controlledTerritoryIndices:
            for connectionId in map.territories[tid].connections:
                if (map.territories[connectionId].owner != self.name):
                    eligableTerritoryIndices.add(tid)  # Add self
                    for c in map.territories[tid].connections:
                        eligableTerritoryIndices.add(c)  # Add connections
                    break
        # Remove territories not controlled by self
        eligableTerritoryIndices = [i for i in eligableTerritoryIndices if i in controlledTerritoryIndices]
        return eligableTerritoryIndices

    def getAllValidPlacements(self, map, armiesToPlace):
        # 1 Get territories connected to enemy territories
        # 2 Get territories connected to those territories
        # 3 Use union set of both to get territories eligable for placement
        eligableTerritoryIndices = self.getTerritoryIndicesEligableForPlacement(map)

        # Limit the amount of eligable territories to 15
        # If more than 15, then pick 15 at random
        # That still gives 1,961,256 choices at 15_C_10 with replacement
        if (len(eligableTerritoryIndices) > 15):
            eligableTerritoryIndices = random.sample(eligableTerritoryIndices, 15)

        # 4 Determine group size for army placement
        groupSize = self.convertArmiesToPlaceToGroupSize(armiesToPlace)

        # 5 Generate all combinations with replacement
        allPlacementCombinations = set(combinations_with_replacement(eligableTerritoryIndices, groupSize))

        return allPlacementCombinations

    def pickBestPlacementOrder(self, map, armiesToPlace, groupSize=None):
        # Change in mindset - why consider placing them all at once?
        # Build it up slowly to prune away bad placements early on.
        if (groupSize == None):
            groupSize = self.convertArmiesToPlaceToGroupSize(armiesToPlace)

        placementOrder = []
        armiesPlaced = 0
        while (armiesToPlace < armiesPlaced):
            if (armiesPlaced + groupSize > armiesToPlace):
                groupSize = armiesToPlace - armiesPlaced

            bestScore = float('-inf')
            bestTerritoryPlacement = None
            eligableTerritoryIndices = self.getTerritoryIndicesEligableForPlacement(map)
            # Mix up the ordering a bit to prevent armies from going to the same territory in the event of a tie
            random.shuffle(eligableTerritoryIndices)
            for eligableTerritoryIndex in eligableTerritoryIndices:
                tmp_map = map.getCopy()
                tmp_map.placeArmy(self.name, groupSize, eligableTerritoryIndex)
                score = self.scoreGameState(tmp_map)
                if (score > bestScore):
                    bestScore = score
                    bestTerritoryPlacement = eligableTerritoryIndex
            placementOrder.append((bestTerritoryPlacement, groupSize))  # Tuple: (TerritoryId, armiesToPlace)
        return placementOrder

    def getPreferredPlacementOrder(self, map, armiesToPlace):
        tmpMap = map.getCopy()
        order = []
        for i in range(armiesToPlace):
            order.append(self.placeUnit(tmpMap))
        return order

    def placeArmiesInOrder(self, map, order, armiesToPlace=None):
        if(order == None):
            return
        if (armiesToPlace == None):
            for item in order:
                territoryIndex = item[0]
                armiesToPlace = item[1]
                map.placeArmy(self.name, armiesToPlace, territoryIndex)
        else:
            groupSize = self.convertArmiesToPlaceToGroupSize(armiesToPlace)
            for item in order:
                if (item == None):
                    continue
                territoryIndex = item
                if (armiesToPlace - groupSize > 0):
                    atp = groupSize
                    armiesToPlace -= groupSize
                else:
                    atp = armiesToPlace
                map.placeArmy(self.name, atp, territoryIndex)

    def getAllValidMovements(self, map):
        controlledTerritoryIndices = [t.index for t in map.getTerritoriesByPlayer(self.name)]
        controlledTerritoriesThatCanMove = [ t for t in controlledTerritoryIndices if map.territories[t].getArmy() > 1]

        allValidMovements = []

        for sourceId in controlledTerritoriesThatCanMove:
            possibleTargets = [i for i in map.territories[sourceId].connections if i in controlledTerritoryIndices]
            for targetId in possibleTargets:
                allValidMovements.append((sourceId, targetId))

        return allValidMovements

    def convertArmyPercentageToAmount(self, armiesOnTerritory, percentage):
        percentage = max(0, min(1, percentage))  # Clamp the percentage between 0-1
        armiesOnTerritory -= 1  # Always keep 1 on the supplying territory
        unitsToTransfer = math.floor(armiesOnTerritory * percentage)
        # Ensure that unitsToTransfer is non-negative
        unitsToTransfer = max(unitsToTransfer, 0)
        return unitsToTransfer

    def pickBestMovement(self, map):
        # Check if the bestmovement has already been cached for this map/game state
        mapHash = map.getHash()
        if mapHash in self.bestMovementCache:
            return self.bestMovementCache[mapHash]
        # If not cached, continue as normal
        validMovements = self.getAllValidMovements(map)
        transferPercentages = [0.25, 0.5, 0.75, 1]
        # Assume that the best score is not moving at all until proven otherwise
        bestScore = self.scoreGameState(map)
        bestMovementSupplyId = None
        bestMovementTargetId = None
        bestMovementAmount = None
        for movement in validMovements:
            for transferPercent in transferPercentages:
                tmp_map = map.getCopy()
                amount = tmp_map.territories[movement[0]].getArmy()
                amount = self.convertArmyPercentageToAmount( amount, transferPercent)
                tmp_map.moveArmies(movement[0], movement[1], amount)
                score = self.scoreGameState(tmp_map)
                if (score > bestScore):
                    bestScore = score
                    bestMovementSupplyId = movement[0]
                    bestMovementTargetId = movement[1]
                    bestMovementAmount = amount
        # Cache best movement before continuing
        moveSelected = MoveSelection(bestMovementSupplyId, bestMovementTargetId,bestMovementAmount)
        self.bestMovementCache[mapHash] = moveSelected
        return moveSelected

    def getAllValidAttacks(self, map):
        controlledTerritoryIndices = [t.index for t in map.getTerritoriesByPlayer(self.name)]
        controlledTerritoriesThatCanAttack = [t for t in controlledTerritoryIndices if map.territories[t].getArmy() > 1]

        allValidAttacks = []

        for sourceId in controlledTerritoriesThatCanAttack:
            possibleTargets = [i for i in map.territories[sourceId].connections if i not in controlledTerritoryIndices]
            for targetId in possibleTargets:
                allValidAttacks.append((sourceId, targetId))
        return allValidAttacks

    def getAllValidAttackOrders(self, map, atkSys, maxAttacks=5):
        # Check if a cached version exist, and return it if so
        mapHash = map.getHash()
        if mapHash in self.allValidAttackOrdersCache:
            return self.allValidAttackOrdersCache[mapHash]
        # If not cached, continue as normal
        # Don't permute all valid attacks, only permute the top 10 good ones
        #rm allValidAttacks = self.getAllValidAttacks(map)
        allGoodAttacks = self.getBestAttacksRanked(map, atkSys)[:10]
        allAttackOrderings = []
        for i in range(maxAttacks):
            #rm attackOrderings = permutations(allValidAttacks, i)
            attackOrderings = permutations(allGoodAttacks, i)
            for attackOrder in attackOrderings:
                allAttackOrderings.append(attackOrder)
        # Cache allAttackOrderings before returning
        self.allValidAttackOrdersCache[mapHash] = allAttackOrderings
        return allAttackOrderings

    def getBestAttacksRanked(self, map, atkSys):
        validAttacks = self.getAllValidAttacks(map)
        attacks = []

        for attack in validAttacks:
            tmp_map = map.getCopy()
            territory = tmp_map.territories[attack[0]]
            enemyTerritory = tmp_map.territories[attack[1]]

            attackEstimate = atkSys.getAttackEstimate(territory.getArmy(), enemyTerritory.getArmy())

            if (attackEstimate.attackers > 0 and attackEstimate.attackSuccessChance > 0.1):
                territory.setArmy(attackEstimate.attackers)
                if (attackEstimate.defenders <= 0):
                    enemyTerritory.owner = self.name
                    enemyTerritory.setArmy(1)
            else:
                continue

            score = math.ceil(self.scoreGameState(tmp_map) * attackEstimate.attackSuccessChance)

            attacks.append((score, attack))

        attacks.sort(key=lambda y: y[0], reverse=True)  # Sort based on score
        # Break apart tuple so that only the (source, target) tuple remains
        attacks = [x[1] for x in attacks]
        return attacks
        #rm return AttackSelection(bestAttackId, bestTargetId, bestEstimateResult)

    def pickBestAttack(self, map, atkSys):
        validAttacks = self.getAllValidAttacks(map)
        bestScore = float('-inf')
        bestAttackId = None
        bestTargetId = None
        bestEstimateResult = None
        for attack in validAttacks:
            tmp_map = map.getCopy()
            territory = tmp_map.territories[attack[0]]
            enemyTerritory = tmp_map.territories[attack[1]]

            attackEstimate = atkSys.getAttackEstimate(territory.getArmy(), enemyTerritory.getArmy())

            if (attackEstimate.attackers > 0):
                enemyTerritory.owner = self.name
                territory.setArmy(attackEstimate.attackers)
                enemyTerritory.setArmy(1)
            else:
                continue

            score = math.ceil(
                self.scoreGameState(tmp_map) * attackEstimate.attackSuccessChance)
            if (score > bestScore):
                bestScore = score
                bestAttackId = territory.index
                bestTargetId = enemyTerritory.index
                bestEstimateResult = attackEstimate

        return AttackSelection(bestAttackId, bestTargetId, bestEstimateResult)

    def scoreGameState(self, map):
        # Return cached score of map/game state if it exists
        mapHash = map.getHash()
        playerHash = self.getHash_ConsiderationOnly()
        if mapHash in self.scoreGameStateCache:
            return self.scoreGameStateCache[mapHash]
        
        # If a cached version doesn't exist, then continue as normal
        armyCount = 0
        playerControlledTerritories = map.getTerritoriesByPlayer(self.name)
        territoryCount = len(playerControlledTerritories)
        remainingPlayers = map.getPlayerCount()

        enemyArmyAdjacent = 0
        enemyTerritoryAdjacent = 0
        armyEnemyAdjacent = 0
        territoryEnemyAdjacent = 0
        for territory in playerControlledTerritories:
            armyCount += territory.getArmy()
            thisTerritoryValuesIncluded = False
            for tid in territory.connections:
                if (map.territories[tid].owner != self.name and not thisTerritoryValuesIncluded):
                    armyEnemyAdjacent += territory.getArmy()
                    territoryEnemyAdjacent += 1
                    thisTerritoryValuesIncluded = True
                if(map.territories[tid].owner != self.name):
                    enemyTerritoryAdjacent += 1
                    enemyArmyAdjacent += map.territories[tid].getArmy()


        armyUpkeep = map.getNewUnitCountForPlayer(self.name)
        continents = map.getCountOfContinentsControlledByPlayer(self.name)

        score = 0
        score += armyCount * self.characteristics["Consideration"]["Armies"].value
        score += territoryCount * self.characteristics["Consideration"]["Territories"].value
        score += armyEnemyAdjacent * self.characteristics["Consideration"]["Armies Enemy Adjacent"].value
        score += territoryEnemyAdjacent * self.characteristics["Consideration"]["Territories Enemy Adjacent"].value
        score += armyUpkeep * self.characteristics["Consideration"]["Army Upkeep"].value
        score += continents * self.characteristics["Consideration"]["Continents"].value
        score += remainingPlayers * self.characteristics["Consideration"]["Remaining Players"].value
        score += enemyArmyAdjacent * self.characteristics["Consideration"]["Enemy Armies Adjacent"].value
        score += enemyTerritoryAdjacent * self.characteristics["Consideration"]["Enemy Territories Adjacent"].value
        
        # Cache the final score before returning
        self.scoreGameStateCache[mapHash] = score
        return score
