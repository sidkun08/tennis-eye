from objects.ballObject import TennisBall
import numpy as np
class Tracker:
    def __init__(self):
        self.previousFrame = None
        self.currentFrame = None
        self.velocity = (0,0)
        self.trajectory = []
        self.missedFrames = 0

    def update(self, coords):
        if coords == None:
            self.missedFrames += 1
            return 
        self.trajectory.append(coords)
        numOfFrames = len(self.trajectory)
        if numOfFrames > 1:
            self.previousFrame = self.trajectory[numOfFrames-2]
            self.currentFrame = self.trajectory[numOfFrames-1]
        elif numOfFrames == 1:
            self.currentFrame = self.trajectory[numOfFrames-1]

    def getPrevious(self):
        return self.previousFrame
    
    def getCurrent(self):
        return self.currentFrame

    def findVelocity(self):
        self.currentFrame