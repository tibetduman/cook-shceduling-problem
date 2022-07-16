"""
Point class to represent cities/stations
"""
import math
SPEED = 1.5
### Values in parantheses are average of 10 problems solved with Convexhull Heuristic with
### the given speed.
# For small problems: 0.85 (146.22), 1.5 (91.84), 2.5 (70.68)
# For medium problems: 0.5 (354), 0.92 (217.74), 1.5 (171.71)
# For large problems: 0.38 (635), 0.7 (395), 1 (339)

class Point:

    def __init__(self, x: float, y: float):
        """Given x and y coordinates generates a Point object representing it."""
        self.x = x
        self.y = y

    ### Distance Methods
    @staticmethod
    def chebyshev_distance(p1: 'Point', p2: 'Point'):
        """Given two points p1 and p2 returns their chebyshev distance."""
        return (max(abs(p1.x - p2.x), abs(p1.y - p2.y))) / SPEED
 
    @staticmethod
    def euclidian_distance(p1: 'Point', p2: 'Point'):
        """Given two points p1 and p2 returns their euclidian distance."""
        return (math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)) / SPEED

    def __eq__(self, other: 'Point') -> bool:
        """Given another point checks if they represent the same point."""
        return type(self) == type(other) and self.x == other.x and self.y == other.y
    
    def __hash__(self) -> int:
        return hash((self.x, self.y))
    
    def __str__(self) -> str:
        return str(self.x) + " " + str(self.y)