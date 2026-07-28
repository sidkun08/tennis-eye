class Tracker:
    def __init__(self):
        self.previousPos = None
        self.currentPos = None
        self.velocity = (0,0)
        self.trajectory = []
        self.missedFrames = 0

    def update(self, coords):
        if coords == None:
            self.missedFrames += 1
            return 
        self.trajectory.append(coords)
        numOfPos = len(self.trajectory)
        if numOfPos > 1:
            self.previousPos = self.trajectory[numOfPos-2]
            self.currentPos = self.trajectory[numOfPos-1]
        elif numOfPos == 1:
            self.currentPos = self.trajectory[numOfPos-1]

        return self.previousPos, self.currentPos

    def getPrevious(self):
        return self.previousFrame
    
    def getCurrent(self):
        return self.currentFrame

    def findVelocity(self):
        Lx, Ly = self.previousPos
        Fx, Fy = self.currentPos
        velocityX  = Fx-Lx
        velocityY = Fy-Ly
        self.findVelocity = velocityX, velocityY
        return self.findVelocity