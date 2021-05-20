
class TournamentEntry:
    def __init__(self, agent=None):
        self.agent = agent
        self.wins = 0
        self.losses = 0
        self.score = 0

    def __str__(self):
        return f"<{self.agent}, w:{self.wins}, l:{self.losses}, score:{self.score}>"


class Tournament:
    def __init__(self):
        self.entries = []

    def addToTournament(self, agent):
        self.entries.append(TournamentEntry(agent))
