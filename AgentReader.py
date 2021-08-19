import sys
import json
import os.path
from Agent import Agent
from Agent import AgentCharacteristic


class AgentReader():

    @staticmethod
    def readAgent(filePath):
        # Load in map data as JSON
        f = open(filePath)
        rawData = f.read()
        f.close()
        data = json.loads(rawData)
        # f.close()

        agent = Agent()

        agent.name = data["name"]
        agentCharacteristicCategories = data["characteristics"].keys()
        for categoryName in agentCharacteristicCategories:
            agent.characteristics[categoryName] = {}
            characteristicsInCategory = data["characteristics"][categoryName]
            for characteristicName, characteristicData in characteristicsInCategory.items():
                agent.characteristics[categoryName][characteristicName] = AgentReader.dictionaryToCharacteristic(
                    characteristicData)
        return agent

    @staticmethod
    def dictionaryToCharacteristic(charDict):
        # TODO: Validate these values
        value = float(charDict["value"])
        adjustmentAmt = float(charDict["adjustmentAmount"])
        description = str(charDict["description"])
        return AgentCharacteristic(value, description, adjustmentAmt)
