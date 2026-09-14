import numpy as np
import json

class Tracker:
    def __init__(self):
        self.previousPos = None
        self.currentPos = None
        self.velocity = (0,0)
        self.trajectory = []
        self.missedFrames = 0
        self.markPos = None

    def getPrevious(self):
        return self.previousPos
    
    def getCurrent(self):
        return self.currentPos
    
    def getTrajectory(self):
        return list(self.trajectory)
    
    def reset(self):
       return self.__init__()
    
    def getMissedFrames(self):
        return self.missedFrames

    def getVelocity(self):
        return self.velocity


    def getDy(self):
        return self.velocity[1]

    def getDx(self):
        return self.velocity[0]

    def update(self, coords):
        if coords is None:
            self.missedFrames += 1
            return 
        self.missedFrames = 0
        self.trajectory.append(coords)
        numOfPos = len(self.trajectory)
        if numOfPos > 1:
            self.previousPos = self.trajectory[numOfPos-2]
            self.currentPos = self.trajectory[numOfPos-1]
            self.findVelocity()
        elif numOfPos == 1:
            self.currentPos = self.trajectory[numOfPos-1]

        self.frame_count += 1
        return self.trajectory

    def track_continuity(self, coords, id):
        self.continuity[coords] = id
        return self.continuity

    def delete_coords(self, coords):
        self.trajectory.remove(coords)
        return self.trajectory

    def get_mark_pos(self):
        return self.markPos

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
        return self.currentPos


    def getPredicted(self):
        Lx, Ly = self.getCurrent()
        velocity = self.getVelocity()
        predicedPos = (Lx + velocity[0]), (Ly + velocity[1])
        return predicedPos
