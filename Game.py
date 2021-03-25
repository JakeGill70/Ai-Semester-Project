import pygame
from Map import Map
import sys
import random
import math
import time
from collections import deque
from Interpolation import Interpolation


class Game():
    def __init__(self):
        self.width = 800
        self.height = 600
        self.font = None

    def drawCircle(self, screen, color, x, y, radius=20):
        pygame.draw.circle(screen, color, (x, y), radius)

    def drawLine(self, screen, color, posA, posB, width=3):
        pygame.draw.line(screen, color, posA, posB, width)

    def drawLine_blended(self, screen, colorA, colorB, posA, posB, interpolationSteps=10, thickness=2):
        for x in range(1, interpolationSteps):
            p = x/interpolationSteps
            p_less = p - (1/interpolationSteps)
            color = Interpolation.interpolateTuple(colorA, colorB, p)

            start = Interpolation.interpolateTuple(posA, posB, p_less)
            end = Interpolation.interpolateTuple(posA, posB, p)
            self.drawLine(screen, color, start, end, thickness)

    def drawInfo(self, screen, map):
        for territory in map.territories.values():
            info = f"{territory.owner}:{territory.army}"
            label = self.font.render(info, False, (255, 255, 255, 255), (0, 0, 0, 120))
            pos = territory.position
            size = self.font.size(info)
            screen.blit(label, (pos[0]-size[0]/2, pos[1]-size[1]/2))

    def drawNodes(self, screen, map, nodeSize):
        for territory in map.territories.values():
            color = map.continentColors[territory.continent]
            self.drawCircle(screen, color, territory.position[0], territory.position[1], nodeSize)

    def drawConnections(self, screen, map):
        for territory in map.territories.values():
            for connectingIndex in territory.connections:
                connectingTerritory = map.territories[connectingIndex]
                colorA = map.continentColors[territory.continent]
                colorB = map.continentColors[connectingTerritory.continent]
                posA = territory.position
                posB = connectingTerritory.position

                # Colors of two nodes are the same, just draw the line
                if(colorA == colorB):
                    self.drawLine(screen, colorA, posA, posB, 2)
                else:
                    self.drawLine_blended(screen, colorA, colorB, posA, posB)

    def drawMap(self, screen, map):

        nodeRadius = 20
        self.drawNodes(screen, map, nodeRadius)
        self.drawConnections(screen, map)
        self.drawInfo(screen, map)

        pygame.display.update()

    def showWindow(self, map):

        screen = pygame.display.set_mode((self.width, self.height))

        if(not self.font):
            pygame.font.init()  # you have to call this at the start,
            # if you want to use this module.
            self.font = pygame.font.SysFont('monospace', 14)

        self.drawMap(screen, map)

        isDrawingMap = True
        while(isDrawingMap):

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    isDrawingMap = False
