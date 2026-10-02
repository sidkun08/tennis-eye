class Player():
    def __init__(self, name, age, utr):
        self.name = name
        self.age = age
        self.utr = utr
        self.point_score = 0
        self.game_score = 0
        self.set_score = 0
        self.count = 0

    def getName(self):
        return self.name

    def getAge(self):
        return self.age

    def getUtr(self):
        return self.utr

    def get_point_score(self):
        return self.score

    def get_game_score(self):
        return self.game_score
    
    def get_set_score(self):
        return self.set_score

    def change_score(self):
        current_score = self.score
        if current_score == 40:
            check_for_deuce = True
            return check_for_deuce
        elif current_score < 30:
            self.score += 15
        self.score += 10
        return self.score

    def win_score(self):
        self.score += 5
        


class Score_Manager():
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.score1 = 0
        self.score2 = 0
        self.currentSet_p1 = 0
        self.currentSet_p2 = 0
        self.currentGame_p1 = 0
        self.currentGame_p2 = 0

    def get_score_player_one(self):
        return self.score1

    def get_score_player_two(self):
        return self.score2
    
    def update_score(self, player):
        score_update = player.change_score()
        if score_update == True:
            deuce_check = self.check_for_deuce()
            return deuce_check

    def win_game(self, player):
        player.win_score()

    def check_for_deuce(self, player1, player2):
        current_p1_score = player1.get_point_score()
        current_p2_score = player2.get_point_score()
        if current_p1_score == current_p2_score:
            return True
        else:
            return False

