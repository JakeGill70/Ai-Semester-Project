from enum import Enum


class MessageTypes(Enum):
    GuiBuild = 1
    GuiMirror = 2
    AttackResult = 3
    AttackStopNotice = 4
    GameStartNotice = 5
    DuplicatePlayerWarning = 6
    TurnStartNotice = 7
    UnitPlacementNotice = 8
    UnitMovementNotice = 9
    PlayerDefeatedNotice = 10
    PlayerVictoryNotice = 11
    TurnLimitReachedNotice = 12
    GameResults = 13
    GenerationStartNotice = 14
    MatchStartNotice = 15


class Logger:
    @staticmethod
    def message(messageType, message):
        if(messageType == MessageTypes.GuiMirror):
            pass
        elif(messageType == MessageTypes.GuiBuild):
            pass
        elif(messageType == MessageTypes.AttackStopNotice):
            pass
        elif(messageType == MessageTypes.GuiBuild):
            pass
        else:
            print(message)
