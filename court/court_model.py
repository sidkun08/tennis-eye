class CourtModel:
    COURT_LENGTH = 23.77
    SINGLES_WIDTH = 8.23
    SERVICE_LINE_DISTANCE = 6.40

    def __init__(self):
        self.half_length = self.COURT_LENGTH / 2
        self.singles_half_width = self.SINGLES_WIDTH / 2

    def court_corners(self, mode="singles"):
        half_width = self.singles_half_width
        return [
            (-half_width, -self.half_length),
            (half_width, -self.half_length),
            (half_width, self.half_length),
            (-half_width, self.half_length),
        ]

    def point_in_court(self, x, y):
        return abs(x) <= self.singles_half_width and abs(y) <= self.half_length

    def point_in_boundary(self, x, y, boundary_points):
        """Point-in-polygon test for an arbitrary boundary.

        boundary_points should be a sequence of (x, y) vertices in order.
        """
        vertices = list(boundary_points)
        if len(vertices) < 3:
            raise ValueError("A boundary must have at least 3 vertices.")

        inside = False
        j = len(vertices) - 1
        for i in range(len(vertices)):
            xi, yi = vertices[i]
            xj, yj = vertices[j]

            crossing = ((yi > y) != (yj > y)) and (
                x < (xj - xi) * (y - yi) / (yj - yi) + xi
            )
            if crossing:
                inside = not inside
            j = i

        return inside

    def court_lines(self, mode="singles"):
        """Return named (start, end) line segments for the specified court."""
        half_width = self._boundary_half_width(mode)
        outer_width = self.doubles_half_width
        lines = {
            "left_baseline": ((-half_width, -self.half_length), (half_width, -self.half_length)),
            "right_baseline": ((-half_width, self.half_length), (half_width, self.half_length)),
            "left_singles_sideline": (
                (-self.singles_half_width, -self.half_length),
                (-self.singles_half_width, self.half_length),
            ),
            "right_singles_sideline": (
                (self.singles_half_width, -self.half_length),
                (self.singles_half_width, self.half_length),
            ),
            "left_service_line": (
                (-self.singles_half_width, -self.SERVICE_LINE_DISTANCE),
                (self.singles_half_width, -self.SERVICE_LINE_DISTANCE),
            ),
            "right_service_line": (
                (-self.singles_half_width, self.SERVICE_LINE_DISTANCE),
                (self.singles_half_width, self.SERVICE_LINE_DISTANCE),
            ),
            "center_service_line": (
                (0, -self.SERVICE_LINE_DISTANCE),
                (0, self.SERVICE_LINE_DISTANCE),
            ),
        }
        return lines