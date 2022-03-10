from abc import ABC, abstractmethod
import pygame

class GameGraphics(ABC):
    def __init__(self):
        self.width = 800
        self.height = 600
        self.font = None
        self.initializeFont()

    def initializeFont(self, fontName='monospace', fontSize=14):
        if(not self.font):
            pygame.font.init()  # you have to call this at the start,
            # if you want to use this module.
            self.font = pygame.font.SysFont(fontName, fontSize)
    
    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height

    def getFont(self):
        return self.font

    def drawCircle(self, screen, color, x, y, radius=20):
        pygame.draw.circle(screen, color, (x, y), radius)

    def drawLine(self, screen, color, posA, posB, width=3):
        pygame.draw.line(screen, color, posA, posB, width)

    @abstractmethod
    def showWindow(self, map, windowName, autoCloseTimer):
        pass