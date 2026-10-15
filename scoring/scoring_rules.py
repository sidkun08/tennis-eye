"""Pure tennis scoring rules for singles matches.

This module deliberately contains no live match state. It only evaluates
scoring transitions and produces display labels.
"""

# Standard targets.
NORMAL_GAME_POINTS = 4
SET_GAMES = 6
TIEBREAK_POINTS = 10


class ScoringRules:
    """Reusable functions for conventional tennis scoring."""
    def __init__(self, raw_points, opponent_raw_points):
        self.raw_points = raw_points
        self.opponent_raw_points = opponent_raw_points       
    
    def point_label(self, tiebreak):
        """Return the display label for one player's point score."""
        if tiebreak:
            return str(self.raw_points)

        if self.raw_points <= 0:
            return "0"
        elif self.raw_points == 1:
            return "15"
        elif self.raw_points == 2:
            return "30"

        # Deuce / advantage territory.
        if self.opponent_raw_points >= 3:
            if self.raw_points == self.opponent_raw_points:
                return "40"
            return "45" if self.raw_points > self.opponent_raw_points else "40"

        return "40"

    def game_won(self, tiebreak):
        """Return True if a player has won the current game."""
        if tiebreak:
            return self.raw_points >= TIEBREAK_POINTS and self.raw_points - self.opponent_raw_points >= 2
        return self.raw_points >= NORMAL_GAME_POINTS and self.raw_points - self.opponent_raw_points >= 2

    def should_tiebreak(self, player_games, opponent_games):
        """Return True when a set has reached 6-6 and needs a tiebreak."""
        return player_games == SET_GAMES and opponent_games == SET_GAMES

    def set_won(self, player_games, opponent_games):
        """Return True if a player has won a normal (non-tiebreak) set."""
        winner_games = max(player_games, opponent_games)
        loser_games = min(player_games, opponent_games)
        return winner_games >= SET_GAMES and winner_games - loser_games >= 2

    def match_won(self, player_sets, opponent_sets):
        """Return True if either player has won the match."""
        needed = 2
        return player_sets >= needed or opponent_sets >= needed