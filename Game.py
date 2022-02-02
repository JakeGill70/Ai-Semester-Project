import pygame
from Map import Map
import sys
import random
import math
import time
from collections import deque
from Interpolation import Interpolation
from GameGraphics import GameGraphics


class Game(GameGraphics):
    def __init__(self):
        GameGraphics.__init__(self)

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
            info = str(territory)
            label = self.font.render(info, False, (255, 255, 255, 255), (0, 0, 0, 120))
            pos = territory.position
            size = self.font.size(info)
            screen.blit(label, (pos[0]-size[0]/2, pos[1]-size[1]/2))

    def drawNodes(self, screen, map, nodeSize):
        for territory in map.territories.values():
            color = map.continents[territory.continent].color
            self.drawCircle(screen, color, territory.position[0], territory.position[1], nodeSize)

    def drawConnections(self, screen, map):
        for territory in map.territories.values():
            for connectingIndex in territory.connections:
                connectingTerritory = map.territories[connectingIndex]
                colorA = map.continents[territory.continent].color
                colorB = map.continents[connectingTerritory.continent].color
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

    def showWindow(self, map, windowName="RISK", autoCloseTimer=None):
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(windowName)

        self.initializeFont()

        self.drawMap(screen, map)

        startTime = time.time()

        isDrawingMap = True
        while(isDrawingMap):

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    isDrawingMap = False
                    exit()

            if(autoCloseTimer):
                if(time.time() >= startTime+autoCloseTimer):
                    isDrawingMap = False
