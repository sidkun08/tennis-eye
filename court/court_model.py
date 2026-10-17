"""Singles tennis court geometry. No cameras, no images, no homography.

Meters. Origin is the center of the net.
    x: across the court (singles sidelines at +/- singles_half_width)
    y: along the court (baselines at +/- half_length)
Dimensions are to the OUTER edge of each line.
"""

import math


class CourtModel:
    COURT_LENGTH = 23.77
    SINGLES_WIDTH = 8.23
    SERVICE_LINE_DISTANCE = 6.40

    def __init__(self):
        self.half_length = self.COURT_LENGTH / 2
        self.singles_half_width = self.SINGLES_WIDTH / 2

    def court_corners(self):
        hw = self.singles_half_width
        return [
            (-hw, -self.half_length),
            (hw, -self.half_length),
            (hw, self.half_length),
            (-hw, self.half_length),
        ]

    def point_in_court(self, x, y):
        """Plain geometry only. For line calls use line_decision.py, which
        accounts for ball radius and measurement error."""
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

    def court_lines(self):
        """Named (start, end) line segments for the singles court."""
        sw = self.singles_half_width
        hl = self.half_length
        sl = self.SERVICE_LINE_DISTANCE
        return {
            "left_baseline": ((-sw, -hl), (sw, -hl)),
            "right_baseline": ((-sw, hl), (sw, hl)),
            "left_singles_sideline": ((-sw, -hl), (-sw, hl)),
            "right_singles_sideline": ((sw, -hl), (sw, hl)),
            "left_service_line": ((-sw, -sl), (sw, -sl)),
            "right_service_line": ((-sw, sl), (sw, sl)),
            "center_service_line": ((0, -sl), (0, sl)),
        }

    # ---- geometry used by line_decision.py ----

    @staticmethod
    def distance_to_line(x, y, segment):
        """Shortest distance from a point to a (start, end) line segment."""
        (x1, y1), (x2, y2) = segment
        dx, dy = x2 - x1, y2 - y1
        length_sq = dx * dx + dy * dy
        if length_sq == 0:
            return math.hypot(x - x1, y - y1)
        t = ((x - x1) * dx + (y - y1) * dy) / length_sq
        t = max(0.0, min(1.0, t))
        return math.hypot(x - (x1 + t * dx), y - (y1 + t * dy))

    @staticmethod
    def _cyclic_edges(vertices, names):
        """Named edges v0->v1, v1->v2, ... back to v0, in vertex order."""
        count = len(vertices)
        return {names[i]: (vertices[i], vertices[(i + 1) % count]) for i in range(count)}

    def boundary_edges(self):
        """The four lines that bound the singles playing area for a rally."""
        return self._cyclic_edges(
            self.court_corners(),
            ["left_baseline", "right_singles_sideline",
             "right_baseline", "left_singles_sideline"],
        )

    def service_box(self, lane, net_side):
        """Corners of one service box.

        lane:     +1 or -1, side of the center line (sign of x)
        net_side: +1 or -1, side of the net (sign of y)
        """
        if lane not in (1, -1) or net_side not in (1, -1):
            raise ValueError("lane and net_side must each be +1 or -1")
        sw, sl = self.singles_half_width, self.SERVICE_LINE_DISTANCE
        return [(0, 0), (lane * sw, 0), (lane * sw, net_side * sl), (0, net_side * sl)]

    def service_box_edges(self, lane, net_side):
        return self._cyclic_edges(
            self.service_box(lane, net_side),
            ["net", "singles_sideline", "service_line", "center_service_line"],
        )