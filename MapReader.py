import sys
from Territory import Territory
from Continent import Continent
from Map import Map
import math
import copy
import json
import os.path


class MapReader():

    @staticmethod
    def readMap(filePath):
        '''
        JSON Map Model Definition
        Built using: http://www.objgen.com/json 
        ---------------------------------
        |   agents[]                    |
        |       name string             |
        |       filePath string         |
        |   continents[]                |
        |       name string             |
        |       unitBonus number        |
        |       color[] number          |
        |   territories[]               |
        |       index number            |
        |       connections[] number    |
        |       continent string        |
        |       position[] number       |
        |       owner string            |
        |       armies number           |
        ---------------------------------
        '''
        # Load in map data as JSON
        f = open(filePath)
        data = json.load(f)
        f.close()

        territories = {}
        continents = {}
        agentFilePaths = {}

        # Load agents
        for agentData in data["agents"]:
            agentName = agentData["name"]
            filepath = agentData["filePath"]
            MapReader.validateAgentPath(filepath)
            agentFilePaths[agentName] = filepath

        # Load continents
        for continentData in data["continents"]:
            continentName = continentData["name"]
            unitBonus = int(continentData["unitBonus"])
            color = tuple(continentData["color"])
            continent = Continent(continentName, unitBonus, color)
            MapReader.validateContinent(continent)
            continents[continentName] = continent

        # Load territories
        for territoryData in data["territories"]:
            index = territoryData["index"]
            connections = list(territoryData["connections"])
            continent = territoryData["continent"]
            position = tuple(territoryData["position"])
            owner = territoryData["owner"]
            armies = territoryData["armies"]
            territory = Territory(index, connections, continent, position, owner, armies)
            MapReader.validateTerritory(territory, territories, continents, agentFilePaths)
            territories[index] = territory

        MapReader.validateTerritoryConnections(territories)

        map = Map()
        map.territories = territories
        map.continents = continents

        return map

    @staticmethod
    def validateAgentPath(path):
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Agent file does not exists at \"{os.path.abspath(path)}\".")

    @staticmethod
    def validateContinent(continent):
        if(len(continent.color) != 3):
            raise ValueError(f"Issue with {continent.name}'s color schema. Color must be in RGB format range 0-255.")
        if((continent.color[0] < 0 or continent.color[0] > 255) or (continent.color[1] < 0 or continent.color[1] > 255) or (continent.color[2] < 0 or continent.color[2] > 255)):
            raise ValueError(f"Issue with {continent.name}'s color schema. Color must be in RGB format range 0-255.")
        if(continent.unitBonus < 0):
            raise ValueError(f"Issue with {continent.name}'s unit bonus. Value cannot be less than 0.")

    @staticmethod
    def validateTerritory(territory, territories, continents, agentFilePaths):
        if(territory.index in territories.keys()):
            raise ValueError(
                f"Issue with territory {territory.index}'s index. A territory already exists at index {territory.index}")
        if(territory.continent not in continents.keys()):
            raise ValueError(
                f"Issue with territory {territory.index}'s continent. Continent \"{territory.continent}\" does not exist.")
        if(territory.owner and territory.owner not in agentFilePaths.keys()):
            raise ValueError(
                f"Issue with territory {territory.index}'s owner. Agent \"{territory.owner}\" does not exist.")
        if(territory.getArmy() < 0):
            raise ValueError(
                f"Issue with territory {territory.index}'s army. A territory's army count cannot be less than 0.")

    @staticmethod
    def validateTerritoryConnections(territories):
        for territory in territories.values():
            for connectingIndex in territory.connections:
                connectingTerritory = territories[connectingIndex]
                if(territory.index not in connectingTerritory.connections):
                    raise ValueError(
                        f"Uni-directional connection found. {territory.index } is connected to {connectingIndex}, but {connectingIndex} is not connected to {territory.index}.")
