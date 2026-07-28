class TennisBall:
    def __init__(self, center_x, center_y, radius, contour, circularity):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.contour = contour
        self.circularity = circularity

    def getRadius(self):
        return self.radius
    
    def getX(self):
        return self.center_x
    
    def getY(self):
        return self.center_y
    
    def getContour(self):
        return self.contour
    
    def getCircularity(self):
        return self.circularity
    
    