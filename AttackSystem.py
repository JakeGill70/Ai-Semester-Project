from fractions import Fraction
import random
import time
import math
from collections import namedtuple

AttackResult = namedtuple('AttackResult', 'attackers defenders')
AttackEstimateResult = namedtuple('AttackEstimateResult',
                                  'attackers defenders attackSuccessChance')


class AttackSystem:
    def __init__(self):
        self.knownAttackSuccessEstimates = []
        self.knownAttackRemainingEstimates = []
        self.knownDefendRemainingEstimates = []

        self.readAttackRemainingStatistics("AttackRemainingStatistics.csv")
        self.readAttackSuccessStatistics("AttackSuccessStatistics.csv")
        self.readDefendRemainingStatistics("DefendRemainingStatistics.csv")

    def readAttackRemainingStatistics(self, filePath):
        '''
            CSV generated from the floor of the average remaining
            units in 1000 battle simulations run by this program
        '''
        f = open(filePath, "r")

        data = []
        for line in f:
            lineData = line.split(",")
            rowData = []
            for i in range(len(lineData)):
                rowData.append(float(lineData[i].strip()))
            data.append(rowData)
        f.close()

        self.knownAttackRemainingEstimates = data

    def readDefendRemainingStatistics(self, filePath):
        '''
            CSV generated from the floor of the average remaining
            units in 1000 battle simulations run by this program
        '''
        f = open(filePath, "r")

        data = []
        for line in f:
            lineData = line.split(",")
            rowData = []
            for i in range(len(lineData)):
                rowData.append(float(lineData[i].strip()))
            data.append(rowData)
        f.close()

        self.knownDefendRemainingEstimates = data

    def readAttackSuccessStatistics(self, filePath):
        '''
            CSV generated from this dataset:
            http://www.cs.man.ac.uk/~iain/riskstats.php
        '''
        f = open(filePath, "r")

        data = []
        for line in f:
            lineData = line.split(",")
            rowData = []
            for i in range(len(lineData)):
                rowData.append(float(lineData[i].strip()))
            data.append(rowData)
        f.close()

        self.knownAttackSuccessEstimates = data

    def getAttackEstimate(self, attackCount, defendCount):
        attackCount = int(attackCount)
        defendCount = int(defendCount)
        if (attackCount < 1 or defendCount < 1):
            raise Exception(f"Error: attackCount/defendCount is is not valid: {attackCount},{defendCount}")

        originalAttackCount = attackCount
        originalDefendCount = defendCount
        estimateSuccess = 0
        estimateAttackRemaining = 0
        estimateDefendRemaining = 0
        # Get the estimate if it exist
        if (attackCount < 30 and defendCount < 30):
            estimateSuccess = self.knownAttackSuccessEstimates[defendCount][attackCount]
            estimateAttackRemaining = self.knownAttackRemainingEstimates[defendCount][attackCount]
            estimateDefendRemaining = self.knownDefendRemainingEstimates[defendCount][attackCount]
        else:
            # Determine a proportional estimate
            reducedEstimateFound = False
            while (not reducedEstimateFound):
                # Consider the ratio of attackingCount to defendCount
                x = Fraction(attackCount, defendCount)
                # Use the reduced fraction of that ratio
                attackCount = x.numerator
                defendCount = x.denominator
                
                # If that reduced ratio exist, then use that to make an estimate
                if (x.numerator < 30 and x.denominator < 30):
                    estimateSuccess = self.knownAttackSuccessEstimates[defendCount][attackCount]
                    estimateAttackRemaining = math.floor((self.knownAttackRemainingEstimates[defendCount][attackCount] / attackCount) * originalAttackCount)
                    estimateDefendRemaining = math.floor((self.knownDefendRemainingEstimates[defendCount][attackCount] / defendCount) * originalDefendCount)
                    reducedEstimateFound = True
                else:
                    # If the reduced ratio doesn't exist, then subtract 1 from both
                    attackCount -= 1
                    defendCount -= 1
                # If the attacker runs out of units first, then assume that the attack has a 100% failure rate
                if (attackCount == 0):
                    estimateSuccess = 0
                    estimateAttackRemaining = 0
                    estimateDefendRemaining = defendCount
                    reducedEstimateFound = True
        # If defender runs out of units first, then assume that the attack has a 100% success rate
                if (defendCount == 0):
                    estimateSuccess = 1
                    estimateAttackRemaining = attackCount
                    estimateDefendRemaining = 0
                    reducedEstimateFound = True

        return AttackEstimateResult(estimateAttackRemaining, estimateDefendRemaining, estimateSuccess)

    def attack(self, attackCount, defendCount, maxAttackLoses, attackArmyMax, defendArmyMax):
        isAttackOver = False
        while (not isAttackOver):
            result = self.battle(attackCount, defendCount, attackArmyMax, defendArmyMax)
            attackCount = result[0]
            defendCount = result[1]
            if (attackCount == 0 or defendCount == 0 or attackCount <= maxAttackLoses):
                isAttackOver = True
        return AttackResult(attackCount, defendCount)

    def battle(self, attackCount, defendCount, attackArmyMax, defendArmyMax):
        # Only let the attacker roll three times
        attackRolls = self.getDiceRolls(attackCount, quick=True)[:attackArmyMax]
        # Only let the defender roll twice
        defendRolls = self.getDiceRolls(defendCount, quick=True)[:defendArmyMax]

        # Get best rolls
        attackRolls.sort(reverse=True)
        defendRolls.sort(reverse=True)

        while (len(defendRolls) > 0 and len(attackRolls) > 0):
            attackValue = attackRolls.pop()
            defendValue = defendRolls.pop()
            if (attackValue <= defendValue):
                attackCount -= 1
            else:
                defendCount -= 1

        return (attackCount, defendCount)

    def rollDice(self):
        return random.randint(1, 6)

    def getDiceRolls(self, amount, quick=False):
        rolls = []
        # Quick getDiceRolls Explained:
        # The normal method iterates for each item in the amount, for programming ease, this is 
        # simply the total number of available armies on a territory. This requires the code to 
        # generate an excessive number of rolls that will simply be truncated upon return
        # because RISK uses at most sets of 3. To use this to our advantage, we only need to 
        # worry about the cases were the amount is 1, 2, 3 or more. This prevents unnecessary
        # iterations that produces a large set that will need to be truncated.
        # TODO: Remember to note this as an optimization in the write-up
        if(quick):
            if (amount >= 1):
                rolls.append(self.rollDice())
            if (amount >= 2):
                rolls.append(self.rollDice())
            if (amount >= 3):
                rolls.append(self.rollDice())
        else:
            for _ in range(amount):
                rolls.append(self.rollDice())
        return rolls


    def getAttackStatistics(self, attackCount, defendCount, runs):
        atkrRemainingCount = 0
        dfdrRemainingCount = 0
        successfulAtkCount = 0
        attackers = 3
        defenders = 2
        for r in range(0, runs):
            result = self.attack(attackCount, defendCount, -1, attackers, defenders)
            atkrRemainingCount += result.attackers
            dfdrRemainingCount += result.defenders
            successfulAtkCount += int(result.defenders <= 0)
        atkrRemainingAvg = math.floor(atkrRemainingCount/runs)
        dfdrRemainingAvg = math.floor(dfdrRemainingCount/runs)
        successfulAtkPercent = successfulAtkCount/runs
        return (atkrRemainingAvg, dfdrRemainingAvg, round(successfulAtkPercent, 3), round(1-successfulAtkPercent, 3))

# ! Uncomment code to generate new attack statistics
# atkSys = AttackSystem()
# runs = 5000
# for atkrs in range(1,31):
#     for dfdrs in range(1,31):
#         stat = atkSys.getAttackStatistics(atkrs, dfdrs, runs)
#         print(f"Atk:{atkrs}, dfd:{dfdrs}, AtkRemAvg:{stat[0]}, DfdRemAvg:{stat[1]}, AtkSucAvg:{stat[2]}, DfdSucAvg:{stat[3]}")

# atkSys = AttackSystem()
# runs = 1000
# avgDef = 0
# avgErr = 0
# totalBattlesCount = 0
# for defenders in range(30, 80):
#     for attackers in range(30, 80):
#         for i in range(runs):
#             estimate = atkSys.getAttackEstimate(attackers, defenders)
#             result = atkSys.attack(attackers, defenders, 0)
#             avgDef += result.defenders
#         totalBattlesCount += 1
#         avgDef = math.floor(avgDef/runs)
#         if(estimate.defenders != 0):
#             error = abs((estimate.defenders - avgDef)) / estimate.defenders
#         else:
#             error = avgDef
#         avgErr += error
#         if(attackers % 10 == 0):
#             print(
#                 f"Atc: {attackers}, Dfc: {defenders}, AvgDef Remaining: {avgDef}, EstDef Remaining: {estimate.defenders}, Err:{error}")

# print(f"Average Error: {avgErr/totalBattlesCount}, Raw Error Total: {avgErr}, Total Battles Count: {totalBattlesCount}")
