
class TournamentEntry:
    def __init__(self, agent):
        self.agent = None
        self.wins = 0
        self.losses = 0
        self.score = 0


class Tournament:
    def __init__(self):
        self.entries = []

    def addToTournament(self, agent):
        self.entries.append(TournamentEntry(agent))
