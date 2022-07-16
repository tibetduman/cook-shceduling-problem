"""The city class for the TSP problem"""
from typing import List
from point import Point

class City:

    def __init__(self, point: Point, process_time: float):
        """Given a point and processing time generates a City object represnting it."""
        self.location = point
        self.process_time = process_time
    
    def distance(self, other_city: 'City'):
        """Given another city return the distance between the two cities."""
        return Point.euclidian_distance(self.location, other_city.location)
    
    def closest_city(self, other_cities:List['City'])->'City':
        """Given other cities returns the closest city, assume other cities is not None."""
        closest = other_cities[0]
        closest_distance = float('inf')
        for city in other_cities:
            dis = self.distance(city)
            if dis < closest_distance:
                closest_distance = dis
                closest = city
        return closest

    def __eq__(self, other: 'City') -> bool:
        """Given another city returns if these two cities represent the same city."""
        return type(self) == type(other) and self.location == other.location and self.process_time == other.process_time

    @staticmethod
    def parse(line: str):
        """Given a line with x y t seperated by spaces returns the corresponding city object."""
        entries = line.split()
        assert len(entries) == 3
        x, y, t = entries
        return City(Point(float(x), float(y)), float(t))
    
    def __hash__(self) -> int:
        return hash((self.location, self.process_time))

    def __repr__(self) -> str:
        return "City at position {0}, {1} with processing time {2}".format(self.location.x, self.location.y, self.process_time)