def is_in(self, bounce_x, bounce_y, match_type="singles"):
        """
        Determines if the calculated bounce coordinate is inbounds.
        Assumes x is the length of the court and y is the width.
        """
        # Check if length is past the baseline
        if abs(bounce_x) > self.half_length:
            return False
            
        # Check width based on match type
        max_width = self.singles_half_width if match_type == "singles" else self.doubles_half_width
        if abs(bounce_y) > max_width:
            return False
            
        return True