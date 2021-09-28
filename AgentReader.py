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
        # Filter "inf" and "-inf" values
        rawData = rawData.replace("-inf", "-1000")
        rawData = rawData.replace("inf", "1000")
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
    def readAgentsFromMapFile(filePath):
        # Load in map data as JSON
        f = open(filePath)
        data = json.load(f)
        f.close()

        agents = []

        # Load agents
        for agentData in data["agents"]:
            agentName = agentData["name"]
            filepath = agentData["filePath"]
            agents.append(AgentReader.readAgent(filePath))

    @staticmethod
    def dictionaryToCharacteristic(charDict):
        value = float(charDict["value"])
        adjustmentAmt = float(charDict["adjustmentAmount"])
        lowerLimit = float(charDict["lowerLimit"])
        upperLimit = float(charDict["upperLimit"])
        description = str(charDict["description"])
        return AgentCharacteristic(value, description, adjustmentAmt, lowerLimit, upperLimit)
