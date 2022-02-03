from abc import ABC, abstractmethod

class StrategyGame(ABC):
    @abstractmethod
    def setupGameBoard(self, agentList):
        pass

    @abstractmethod
    def playGame(self, agents, map):
        pass