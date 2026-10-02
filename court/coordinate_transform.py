TOP_LEFT_CORNER = "corner1"
TOP_RIGHT_CORNER = "corner2"
BASE_LEFT_CORNER = "corner3"
BASE_RIGHT_CORNER = "corner4"


TRANSFORMED_TOP_LEFT_CORNER = (0, 0)
TRANSFORMED_BASE_LEFT_CORNER = (0, 78)
TRANSFORMED_TOP_RIGHT_CORNER = (27, 0)
TRANSFORMED_BASE_RIGHT_CORNER = (27, 78)

CONSTANT_OF_X = abs(TOP_LEFT_CORNER[0] - TRANSFORMED_TOP_LEFT_CORNER[0])
CONSTANT_OF_Y = abs(BASE_RIGHT_CORNER[0] - TRANSFORMED_BASE_RIGHT_CORNER[0])

def get_coords(bounce_coords):
    if bounce_coords is not None:
        x_bounce, y_bounce = bounce_coords
        x_bounce -= CONSTANT_OF_X
        y_bounce -= CONSTANT_OF_Y
        return (x_bounce, y_bounce)
    return None