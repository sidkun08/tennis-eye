"""
display.py

Builds the scoreboard window. No camera feed, no overlays -- just the
current score and the current IN/OUT status, updated reactively.

This module knows nothing about vision, cameras, detection, or how a
decision was reached. It only knows:
  - how to show a score, given score_manager's display-ready dict
  - how to show a decision string ("IN" / "OUT" / "UNCERTAIN")

Wiring:
  score_manager = ScoreManager(on_score_change=window.update_score)
  ...
  window.update_decision_status("OUT")   # call this when a bounce is decided
  score_manager.handle_line_call(is_out=True, hitter="player")  # then this awards the point

Calling these as two separate steps (rather than combining them) means
the status label can show "OUT" for a beat before the score refreshes,
which reads more clearly on a live display than both changing at once.

NOTE: PySide6 must be installed (`pip install PySide6`). It could not be
imported/run in this sandbox since PySide6 isn't available here -- test
it for real on your actual machine. The import is wrapped so this file
can still be *read* and its non-PySide6 pieces reasoned about even
without PySide6 present.
"""

import sys

try:
    from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QLabel
    from PySide6.QtGui import QFont
    from PySide6.QtCore import Qt
    _PYSIDE6_AVAILABLE = True
except ImportError:
    _PYSIDE6_AVAILABLE = False


DECISION_COLORS = {
    "IN": "color: green;",
    "OUT": "color: red;",
    "UNCERTAIN": "color: orange;",
}


class ScoreboardDisplay(QMainWindow if _PYSIDE6_AVAILABLE else object):
    def __init__(self, window_title="Tennis VAR - Scoreboard"):
        if not _PYSIDE6_AVAILABLE:
            raise ImportError("PySide6 is not installed -- run: pip install PySide6")

        super().__init__()
        self.setWindowTitle(window_title)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QGridLayout(central_widget)

        big_font = QFont()
        big_font.setPointSize(36)
        big_font.setBold(True)

        medium_font = QFont()
        medium_font.setPointSize(24)

        status_font = QFont()
        status_font.setPointSize(28)
        status_font.setBold(True)

        self.player_points_label = QLabel("0")
        self.opponent_points_label = QLabel("0")
        self.games_label = QLabel("Games: 0 - 0")
        self.sets_label = QLabel("Sets: 0 - 0")
        self.status_label = QLabel("")  # last IN/OUT/UNCERTAIN call, or match winner, or "Tiebreak"

        self.player_points_label.setFont(big_font)
        self.opponent_points_label.setFont(big_font)
        self.games_label.setFont(medium_font)
        self.sets_label.setFont(medium_font)
        self.status_label.setFont(status_font)

        for label in (self.player_points_label, self.opponent_points_label,
                      self.games_label, self.sets_label, self.status_label):
            label.setAlignment(Qt.AlignCenter)

        layout.addWidget(QLabel("Player"), 0, 0)
        layout.addWidget(QLabel("Opponent"), 0, 1)
        layout.addWidget(self.player_points_label, 1, 0)
        layout.addWidget(self.opponent_points_label, 1, 1)
        layout.addWidget(self.games_label, 2, 0, 1, 2)
        layout.addWidget(self.sets_label, 3, 0, 1, 2)
        layout.addWidget(self.status_label, 4, 0, 1, 2)

    def update_score(self, score_manager):
        """
        Matches the on_score_change callback signature expected by
        score_manager.ScoreManager -- pass this method directly:

            score_manager = ScoreManager(on_score_change=window.update_score)

        Reads score_manager.get_display_score() and refreshes every label.
        """
        score = score_manager.get_display_score()

        self.player_points_label.setText(str(score["player_points"]))
        self.opponent_points_label.setText(str(score["opponent_points"]))
        self.games_label.setText(f"Games: {score['player_games']} - {score['opponent_games']}")
        self.sets_label.setText(f"Sets: {score['player_sets']} - {score['opponent_sets']}")

        if score["match_winner"] is not None:
            self.status_label.setText(f"Match winner: {score['match_winner'].upper()}")
            self.status_label.setStyleSheet("")
        elif score["in_tiebreak"]:
            self.status_label.setText("Tiebreak")
            self.status_label.setStyleSheet("")

    def update_decision_status(self, decision):
        """
        Call this when a bounce's IN/OUT/UNCERTAIN decision is made,
        before awarding the point via score_manager. decision: "IN",
        "OUT", "UNCERTAIN", or None (clears the status text).
        """
        if decision is None:
            self.status_label.setText("")
            self.status_label.setStyleSheet("")
            return

        self.status_label.setText(decision)
        self.status_label.setStyleSheet(DECISION_COLORS.get(decision, ""))


def run_app(window_title="Tennis VAR - Scoreboard"):
    """
    Starts the Qt application and returns (app, window). Call once from
    main.py; feed it updates via window.update_score / update_decision_status
    from wherever your processing loop lives (thread, QTimer, etc.).
    """
    if not _PYSIDE6_AVAILABLE:
        raise ImportError("PySide6 is not installed -- run: pip install PySide6")

    app = QApplication.instance() or QApplication(sys.argv)
    window = ScoreboardDisplay(window_title)
    window.show()
    return app, window


if __name__ == "__main__":
    # Quick manual test: run this file directly (with PySide6 installed)
    # to see the scoreboard window with a fake score fed into it.
    if not _PYSIDE6_AVAILABLE:
        print("PySide6 is not installed in this environment -- install it "
              "and re-run this file to visually test the scoreboard window.")
    else:
        from scoring import score_manager

        app, window = run_app()

        sm = ScoreManager(on_score_change=window.update_score)
        window.update_decision_status("OUT")
        sm.handle_line_call(is_out=True, hitter="player")

        sys.exit(app.exec())