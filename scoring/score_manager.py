from scoring_rules import ScoringRules  # type: ignore
from match_state import MatchState  # type: ignore


class Player:
    def __init__(self, name="Player", age=0, utr=0.0):
        self.name = name
        self.age = age
        self.utr = utr

    def getName(self):
        return self.name

    def getAge(self):
        return self.age

    def getUtr(self):
        return self.utr


class ScoreManager:
    def __init__(
        self,
        on_score_change=None,
        player_name="Player",
        opponent_name="Opponent",
        best_of_sets=3,
        player=None,
        opponent=None,
    ):
        if player is not None:
            player_name = getattr(player, "name", player_name)
        if opponent is not None:
            opponent_name = getattr(opponent, "name", opponent_name)

        self.player = Player(player_name)
        self.opponent = Player(opponent_name)
        self.on_score_change = on_score_change
        self.state = MatchState(best_of_sets=best_of_sets)

    def get_display_score(self):
        state = self.state
        return {
            "player_points": ScoringRules.point_label(
                state.player_points, state.opponent_points, state.in_tiebreak
            ),
            "opponent_points": ScoringRules.point_label(
                state.opponent_points, state.player_points, state.in_tiebreak
            ),
            "player_games": state.player_games,
            "opponent_games": state.opponent_games,
            "player_sets": state.player_sets,
            "opponent_sets": state.opponent_sets,
            "match_winner": state.match_winner,
            "in_tiebreak": state.in_tiebreak,
        }

    def get_score_player_one(self):
        return self.state.player_points

    def get_score_player_two(self):
        return self.state.opponent_points

    def is_match_over(self):
        return self.state.is_match_complete()

    def award_point(self, winner):
        """Award one confirmed point and process all resulting transitions."""
        if self.state.match_complete:
            return self.get_display_score()

        winner = (winner or "").strip().lower()
        if winner in {"player", "p1", "player1", "player_one"}:
            side = "player"
            self.state.player_points += 1
        elif winner in {"opponent", "p2", "player2", "player_two", "other"}:
            side = "opponent"
            self.state.opponent_points += 1
        else:
            raise ValueError(f"Unknown point winner: {winner!r}")

        player_points = self.state.player_points
        opponent_points = self.state.opponent_points

        player_won_game = ScoringRules.game_won(
            player_points, opponent_points, tiebreak=self.state.in_tiebreak
        )
        opponent_won_game = ScoringRules.game_won(
            opponent_points, player_points, tiebreak=self.state.in_tiebreak
        )

        if player_won_game or opponent_won_game:
            game_winner = "player" if player_won_game else "opponent"

            # Tiebreak game wins decide the set immediately.
            if self.state.in_tiebreak:
                if game_winner == "player":
                    self.state.player_sets += 1
                else:
                    self.state.opponent_sets += 1

                self.state.in_tiebreak = False
                self.state.reset_points()
                self.state.reset_games()
                self._after_set_update(game_winner)
            else:
                if game_winner == "player":
                    self.state.player_games += 1
                else:
                    self.state.opponent_games += 1

                self.state.reset_points()
                self.state.current_game_number += 1
                self.state.server = (
                    "opponent" if self.state.server == "player" else "player"
                )

                # Set just finished?
                if ScoringRules.set_won(
                    self.state.player_games, self.state.opponent_games
                ):
                    set_winner = (
                        "player"
                        if self.state.player_games > self.state.opponent_games
                        else "opponent"
                    )
                    if set_winner == "player":
                        self.state.player_sets += 1
                    else:
                        self.state.opponent_sets += 1

                    self.state.reset_games()
                    self.state.current_set_number += 1
                    self.state.current_game_number = 1
                    self._after_set_update(set_winner)

                # Enter tiebreak?
                elif ScoringRules.should_tiebreak(
                    self.state.player_games, self.state.opponent_games
                ):
                    self.state.in_tiebreak = True

            self._check_match_complete()

        self._notify()
        return self.get_display_score()

    def _after_set_update(self, set_winner):
        # Reserved for future set-level bookkeeping (server, history, etc.).
        return set_winner

    def _check_match_complete(self):
        if ScoringRules.match_won(
            self.state.player_sets, self.state.opponent_sets, self.state.best_of_sets
        ):
            self.state.match_complete = True
            self.state.match_winner = (
                "player"
                if self.state.player_sets > self.state.opponent_sets
                else "opponent"
            )

    def handle_line_call(self, is_out=False, hitter="player"):
        """Apply an IN/OUT line call.

        Only an OUT call awards a point, and it goes to the other player.
        An IN call leaves the score unchanged because the rally continues.
        """
        if not is_out:
            return self.get_display_score()

        hitter = (hitter or "player").strip().lower()
        if hitter in {"player", "p1", "player1", "player_one"}:
            winner = "opponent"
        elif hitter in {"opponent", "p2", "player2", "player_two", "other"}:
            winner = "player"
        else:
            raise ValueError(f"Unknown hitter: {hitter!r}")

        return self.award_point(winner)

    def reset_match(self, best_of_sets=None):
        self.state.reset_match(best_of_sets)
        return self.get_display_score()

    def _notify(self):
        callback = self.on_score_change
        if callable(callback):
            callback(self)