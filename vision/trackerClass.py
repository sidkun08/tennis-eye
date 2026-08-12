import numpy as np

class Tracker:
    def __init__(self):
        self.previousPos = None
        self.currentPos = None
        self.velocity = (0,0)
        self.trajectory = []
        self.missedFrames = 0
        self.predicted = False

    def getPrevious(self):
        return self.previousPos
    
    def getCurrent(self):
        return self.currentPos
    
    def getTrajectory(self):
        return list(self.trajectory)

    
    def reset(self):

        self.previousPos = None
        self.currentPos = None
        self.velocity = (0, 0)
        self.trajectory = []
        self.missedFrames = 0


    
    def getMissedFrames(self):
        return self.missedFrames
    
    
    def update(self, coords):
        if coords is None:
            self.missedFrames += 1
            return 
        self.missedFrames = 0
        self.trajectory.append(coords)
        numOfPos = len(self.trajectory)
        if numOfPos > 3:
            self.previousPos = self.trajectory[numOfPos-2]
            self.currentPos = self.trajectory[numOfPos-1]
            self.findVelocity()
        elif numOfPos == 1:
            self.currentPos = self.trajectory[numOfPos-1]

        return self.trajectory
    
    def findVelocity(self):
        if self.previousPos is None:
            return self.velocity 
        Lx, Ly = self.previousPos
        Fx, Fy = self.currentPos
        velocityX  = Fx-Lx
        velocityY = Fy-Ly
        self.velocity = (velocityX, velocityY)
        return self.velocity
    

    def predict(self):
        if self.currentPos is None:
            self.predicted = False
            return None
        
        currentPos = self.getCurrent()
        Lx, Ly = currentPos
        self.currentPos = ((Lx + self.velocity[0]), (Ly + self.velocity[1]))
        self.predicted = True
        return self.currentPos