from fractions import Fraction
import random
import time
import math


class AttackSystem:
    def __init__(self):
        self.knownSuccessEstimates = []
        self.knownRemainingEstimates = []

        self.readAttackRemainingStatistics()
        self.readAttackSuccessStatistics()

    def readAttackRemainingStatistics(self, filePath="AttackRemainingStatistics.csv"):
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

        self.knownRemainingEstimates = data

    def readAttackSuccessStatistics(self, filePath="AttackSuccessStatistics.csv"):
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

        self.knownSuccessEstimates = data

    def getAttackEstimate(self, attackCount, defendCount):

        estimateSuccess = 0
        # Get the estimate if it exist
        if (attackCount < 30 and defendCount < 30):
            estimateSuccess = self.knownSuccessEstimates[defendCount][attackCount]
            estimateAttackRemaining = self.knownRemainingEstimates[defendCount][attackCount]
        else:
            # Determine a proportional estimate
            reducedEstimateFound = False
            while(not reducedEstimateFound):
                # Consider the ratio of attackingCount to defendCount
                x = Fraction(attackCount, defendCount)
                # Use the reduced fraction of that ratio
                attackCount = x.numerator
                defendCount = x.denominator
                # If that reduced ratio exist, then use that to make an estimate
                if (attackCount < 30 and defendCount < 30):
                    estimateSuccess = self.knownSuccessEstimates[defendCount][attackCount]
                    estimateAttackRemaining = self.knownRemainingEstimates[defendCount][attackCount]
                    reducedEstimateFound = True
                else:
                    # If the reduced ratio doesn't exist, then subtract 1 from both
                    attackCount -= 1
                    defendCount -= 1
                # If the attacker runs out of units first, then assume that the attack has a 100% failure rate
                if(attackCount == 0):
                    estimateSuccess = 0
                    estimateAttackRemaining = 0
                    reducedEstimateFound = True
          # If defender runs out of units first, then assume that the attack has a 100% success rate
                if(defendCount == 0):
                    estimateSuccess = 1
                    estimateAttackRemaining = attackCount
                    reducedEstimateFound = True

        return (estimateSuccess, estimateAttackRemaining)

    def attack(self, attackCount, defendCount, maxAttackLoses):
        isAttackOver = False
        while(not isAttackOver):
            result = self.battle(attackCount, defendCount)
            attackCount = result[0]
            defendCount = result[1]
            if(attackCount == 0 or defendCount == 0 or attackCount <= maxAttackLoses):
                isAttackOver = True
            #print(f"Attack Update! atc:{attackCount}, dfc:{defendCount}")
        return (attackCount, defendCount)

    def battle(self, attackCount, defendCount):
        attackRolls = self.getDiceRolls(attackCount)
        # Only let the defender roll twice
        defendRolls = self.getDiceRolls(defendCount)[:2]

        # Get best rolls
        attackRolls.sort()
        defendRolls.sort()

        while(len(defendRolls) > 0 and len(attackRolls) > 0):
            attackValue = attackRolls.pop()
            defendValue = defendRolls.pop()
            if(attackValue <= defendValue):
                attackCount -= 1
            else:
                defendCount -= 1

        return (attackCount, defendCount)

    def rollDice(self):
        return random.randint(1, 6)

    def getDiceRolls(self, amount):
        rolls = []
        if(amount >= 1):
            rolls.append(self.rollDice())
        if(amount >= 2):
            rolls.append(self.rollDice())
        if(amount >= 3):
            rolls.append(self.rollDice())
        return rolls
