import pygame
from Map import Map
import sys
import random
import math
import time
from collections import deque


class Game():
    def __init__(self):
        self.width = 800
        self.height = 600
        self.continentColors = {
            "North America": (255, 255, 0),  # Yellow
            "South America": (255, 0, 0),  # Red
            "Europe": (200, 200, 200),  # Grey
            "Africa": (0, 255, 0),  # Green
            "Asia": (0, 0, 255),  # Blue
            "Australia": (255, 0, 255)  # Pink
        }

    def drawCircle(self, screen, color, x, y, radius=20):
        pygame.draw.circle(screen, color, (x, y), radius)

    def drawLine(self, screen, color, posA, posB, width=3):
        pygame.draw.line(screen, color, posA, posB, width)

    def getRandomPositionAboutCircle(self, x, y, radius=50):
        angle = random.random()*math.pi*2
        cx = math.cos(angle) * radius
        cy = math.sin(angle) * radius
        x += cx
        y += cy
        return (x, y)

    def getDistance(self, posA, posB):
        x1 = posA[0]
        y1 = posA[1]
        x2 = posB[0]
        y2 = posB[1]
        x = (x2-x1)*(x2-x1)
        y = (y2-y1)*(y2-y1)
        return math.sqrt(x+y)

    def addToPositions(self, addedIndex, index, positions, nodeRadius):
        isTouching = True
        maxRadius = (nodeRadius * 2) + 10
        minDist = (nodeRadius * 2) + 10
        while(isTouching):
            # Get random position
            tmpPos = self.getRandomPositionAboutCircle(
                positions[addedIndex][0],
                positions[addedIndex][1],
                maxRadius)
            isTouching = False
            # Bounds check x
            if(tmpPos[0] > self.width-nodeRadius or tmpPos[0]-nodeRadius < 0):
                isTouching = True
                continue
            # Bounds check y
            if(tmpPos[1] > self.height-nodeRadius or tmpPos[1]-nodeRadius < 0):
                isTouching = True
                continue
            # Collision detection
            for key, value in positions.items():
                if(self.getDistance(tmpPos, value) <= minDist):
                    isTouching = True
            maxRadius += 5
        positions[index] = tmpPos

    def getColor(self, index, map):
        continent = map.getContinentOfIndex(index)
        return self.continentColors[continent]

    def getPositions(self, nodeRadius):
        # Use BFS to add nodes to the game board
        # Create psudeo-random positions for each node
        startingNode = 16
        frontier = deque([(startingNode, startingNode)])
        positions = {startingNode: (self.width/2, self.height/2)}

        while(len(frontier) > 0):
            indices = frontier.pop()
            addedIndex = indices[0]
            index = indices[1]

            if(index not in positions):
                self.addToPositions(addedIndex, index, positions, nodeRadius)

            connectedIndices = map.mapData[index].copy()
            random.shuffle(connectedIndices)
            for x in connectedIndices:
                if x not in positions and x not in [n[1] for n in frontier]:
                    frontier.appendleft((index, x))

        return positions

    def drawNodes(self, screen, positions, map, nodeSize):
        for index in map.mapData.keys():
            color = self.getColor(index, map)
            self.drawCircle(screen, color, positions[index][0], positions[index][1], nodeSize)

    def interpolate(self, a, b, p):
        a *= 1.0-p
        b *= p
        return a+b

    def interpolateTuple(self, a, b, p):
        if(len(a) != len(b)):
            print(f"Tuples '{a}' and '{b}' are not the same size")
            return

        values = []
        for i in range(len(a)):
            values.append(self.interpolate(a[i], b[i], p))

        return tuple(values)

    def drawConnections(self, screen, positions, map):
        for index, connections in map.mapData.items():
            for connectingIndex in connections:
                colorA = self.getColor(index, map)
                colorB = self.getColor(connectingIndex, map)
                posA = positions[index]
                posB = positions[connectingIndex]

                if(colorA == colorB):
                    self.drawLine(screen, colorA, posA, posB, 2)
                    continue

                interpolationsteps = 10
                for x in range(1, interpolationsteps):
                    p = x/interpolationsteps
                    p_less = p - (1/interpolationsteps)
                    color = self.interpolateTuple(colorA, colorB, p)

                    start = self.interpolateTuple(posA, posB, p_less)
                    end = self.interpolateTuple(posA, posB, p)
                    self.drawLine(screen, color, start, end, 2)

    def drawMap(self, screen, map):

        nodeRadius = 12
        positions = map.positionData  # self.getPositions(20)
        self.drawNodes(screen, positions, map, nodeRadius)
        self.drawConnections(screen, positions, map)

        pygame.display.update()

    def showWindow(self, map):

        screen = pygame.display.set_mode((self.width, self.height))

        self.drawMap(screen, map)

        isDrawingMap = True

        count = 0

        while(isDrawingMap):

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    isDrawingMap = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pygame.draw.rect(screen, (0, 0, 0), (0, 0, self.width, self.height))
                    # print(event.pos)
                    #self.drawMap(screen, map)
                    print(f"{count}:{str(map.mapData[count])[1:-1]}:{event.pos[0]},{event.pos[1]}")
                    count += 1

        # myfont = pygame.font.SysFont("monospace", 75)


game = Game()
map = Map()
map.readMapData("MapData.txt")
game.showWindow(map)
