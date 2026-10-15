"""State storage for a singles tennis match.

``MatchState`` only stores and resets match data. It does not implement
tennis scoring rules or award points. Those responsibilities belong to
``scoring_rules.py`` and ``score_manager.py``.
"""


class MatchState:
    """Current state of one singles tennis match."""

    def __init__(
        self,
        player_points=0,
        opponent_points=0,
        player_games=0,
        opponent_games=0,
        player_sets=0,
        opponent_sets=0,
        in_tiebreak=False,
        match_complete=False,
        match_winner=None,
        server="player",
        current_set_number=1,
        current_game_number=1,
        best_of_sets=3,
    ):
        self.player_points = player_points
        self.opponent_points = opponent_points
        self.player_games = player_games
        self.opponent_games = opponent_games
        self.player_sets = player_sets
        self.opponent_sets = opponent_sets

        self.in_tiebreak = in_tiebreak
        self.match_complete = match_complete
        self.match_winner = match_winner

        self.server = server
        self.current_set_number = current_set_number
        self.current_game_number = current_game_number
        self.best_of_sets = best_of_sets

    def reset_points(self):
        """Reset only the current point counts."""
        self.player_points = 0
        self.opponent_points = 0

    def reset_games(self):
        """Reset only the current game counts."""
        self.player_games = 0
        self.opponent_games = 0

    def reset_match(self, best_of_sets=None):
        """Restore the state to the beginning of a new match."""
        if best_of_sets is not None:
            self.best_of_sets = best_of_sets
        self.player_points = 0
        self.opponent_points = 0
        self.player_games = 0
        self.opponent_games = 0
        self.player_sets = 0
        self.opponent_sets = 0
        self.in_tiebreak = False
        self.match_complete = False
        self.match_winner = None
        self.server = "player"
        self.current_set_number = 1
        self.current_game_number = 1

    def to_dict(self):
        """Return a consistent dictionary representation of the state."""
        return {
            "player_points": self.player_points,
            "opponent_points": self.opponent_points,
            "player_games": self.player_games,
            "opponent_games": self.opponent_games,
            "player_sets": self.player_sets,
            "opponent_sets": self.opponent_sets,
            "in_tiebreak": self.in_tiebreak,
            "match_complete": self.match_complete,
            "match_winner": self.match_winner,
            "server": self.server,
            "current_set_number": self.current_set_number,
            "current_game_number": self.current_game_number,
            "best_of_sets": self.best_of_sets,
        }

    def is_match_complete(self):
        return self.match_complete