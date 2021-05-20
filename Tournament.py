
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
        self.competitorIndex = 0

    def addToTournament(self, agent):
        self.entries.append(TournamentEntry(agent))

    def getCompetitors(self, groupSize=2):
        competitors = self.entries[self.competitorIndex:(self.competitorIndex+groupSize)]
        self.competitorIndex += groupSize
        self.competitorIndex = self.competitorIndex % len(self.entries)
        return competitors

    def getTournamentTier(self, groupSize=2):
        matchUps = []
        for i in range(0, len(self.entries), groupSize):
            matchUp = self.entries[i:i+groupSize]
            matchUps.append(matchUp)
        return matchUps

    def sortTournament(self):
        # Sort first by losses (low to high),
        # then by score (low to high)
        self.entries.sort(key=lambda x: (x.losses, x.score))

    def removeByMaxLosses(self, maxLosses=1):
        self.entries = [x for x in self.entries if x.losses < maxLosses]

