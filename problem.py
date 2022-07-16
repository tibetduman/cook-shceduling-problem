"""The general problem instance of the TSP."""

from typing import Iterable, Iterator, List
from point import Point
from city import City
from svg import SVGGraphic
from visualize import VisualizationConfig
from scipy.spatial import ConvexHull
import numpy as np

def _next_int(lines: Iterator[str]):
    value = next(lines)
    return int(value)

def remove_comments(lines: Iterable[str]) -> Iterator[str]:
    lines = iter(lines)
    for line in lines:
        if line.startswith("#"):
            continue
        yield line

class Problem:
    grid_side_length = 30

    def __init__(self, cities: List):
        """Given a list of cities generates a corresponding TSP problem."""
        self.cities = cities

    def convexal_cities(self):
        """Returns the convehull cities of the problem, starting from the origin."""
        result = []
        origin = City(Point(0,0), 0)
        points = []
        points.append([origin.location.x, origin.location.y])
        for c in self.cities:
            points.append([c.location.x, c.location.y])
        hull = ConvexHull(points)
        cities = [origin] + self.cities
        for city_num in hull.vertices:
            result.append(cities[city_num])
        # Order the convexhull cities so origin is at the beginning
        before_origin = []
        idx = 0
        while result[idx] != origin:
            before_origin.append(result[idx])
            idx += 1
        return result[idx:] + before_origin


    @staticmethod
    def parse(lines: Iterable[str]):
        """Given lines with the expected format generate a corresponding Problem instance."""
        lines_iter = remove_comments(lines)
        num_cities = _next_int(lines_iter)

        cities = [City.parse(line) for line in lines_iter]
        assert num_cities == len(cities)
        # may want to add an assertion for valid Problem
        return Problem(cities)

    def __repr__(self) -> str:
        result = "Problem cities at: "
        for city in self.cities:
            result += " " + str(city.location)
        return result
    
    def serialize(self, out):
        """Given a solution write out the traversal of the cities at the given file."""
        print(len(self.cities), file=out)
        for city in self.cities:
            print(city.location.x, city.location.y, city.process_time, file=out)

    def visualize_as_svg(self, config: VisualizationConfig) -> SVGGraphic:
        out = SVGGraphic(config.size, config.size)
        out.draw_rect(0, 0, config.size, config.size, 0, "rgb(255, 255, 255)")

        def _rescale(x):
            return  x / self.grid_side_length * config.size

        for c in self.cities:
            out.draw_circle(_rescale(c.location.x), _rescale(
                c.location.y), 4, 0, config.city_color)

        return out

    def visualize_convexal_as_svg(self, config: VisualizationConfig) -> SVGGraphic:
        out = SVGGraphic(config.size, config.size)
        out.draw_rect(0, 0, config.size, config.size, 0, "rgb(255, 255, 255)")

        def _rescale(x):
            return  x / self.grid_side_length * config.size
        convexals = self.convexal_cities()
        print(convexals)
        print(len(convexals))
        for c in self.cities:
            if c in convexals:
                out.draw_circle(_rescale(c.location.x), _rescale(
                    c.location.y), 3, 0, config.convexal_city_color)
            else:
                out.draw_circle(_rescale(c.location.x), _rescale(
                    c.location.y), 3, 0, config.city_color)
        return out
