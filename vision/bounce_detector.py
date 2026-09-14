def bounce_detect(tracker):
    vel = tracker.getVelocity()
    if vel != None:
        dx, dy = tracker.getVelocity()
        derivative = dy/dx
        if abs(dx) > 0:
            while derivative < 0:
                bounce_x, bounce_y = tracker.getPrevious()
            return (bounce_x, bounce_y)

        return None
    return None