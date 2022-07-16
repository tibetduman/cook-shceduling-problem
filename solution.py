"""The solution class for the TSP problem"""
from typing import List
from city import City
from problem import Problem
from point import Point
from svg import SVGGraphic
from visualize import VisualizationConfig
from random import random

class Solution:
    grid_side_length = 30

    def __init__(self, problem: Problem, order: List):
        """Given a traversal order and problem instance create a solution instance."""
        self.problem = problem
        self.order = order
        self.cost = self.calculate_cost()
    
    def valid(self)-> bool:
        """Given a solution checks if it's valid under the TSP definitions."""
        # Check that exactly n cities are visited
        if len(self.order) != len(self.problem.cities):
            return False
        # Check that each city is visited
        if set(self.order) != set(self.problem.cities):
            return False
        return True
    """
    def cost(self):
        total = remaining = distance = 0
        origin = City(Point(0, 0), 0)
        traversal = [origin] + self.order.copy() + [origin]
        k = 1
        while k < len(traversal):
            travel_time = traversal[k - 1].distance(traversal[k])
            total = distance + max(remaining + traversal[k - 1].process_time, travel_time)
            ### Update for next iteration
            remaining = max(0, remaining + traversal[k - 1].process_time - travel_time)
            distance += travel_time
            k += 1
        return total
    """

    def calculate_cost(self):
        """Given a solution calculates it's cost as specified by the cook problem"""
        total = 0
        origin = City(Point(0, 0), 0)
        traversal = [origin] + self.order.copy() + [origin]
        k = 1
        while k < len(traversal):
            total += max(traversal[k - 1].distance(traversal[k]), traversal[k - 1].process_time)
            k += 1
        return round(total, 3)

    def dominates(self):
        """Given a solution returns the ratio of how many times cooking time dominates over travelling time."""
        cook_time_dominates = 0
        origin = City(Point(0, 0), 0)
        traversal = [origin] + self.order.copy() + [origin]
        k = 1
        while k < len(traversal):
            if traversal[k - 1].process_time > traversal[k - 1].distance(traversal[k]):
                cook_time_dominates += 1
            k += 1
        return cook_time_dominates / len(self.problem.cities)

    def random_neighbor(self):
        """Given solution finds a neighboring solution by swaping the order of two random cities"""
        rc_index1, rc_index2 = int(random() * len(self.order)), int(random() * len(self.order))
        resulting_cities = self.order.copy()
        resulting_cities[rc_index1], resulting_cities[rc_index2] = resulting_cities[rc_index2], resulting_cities[rc_index1]
        return Solution(self.problem, resulting_cities)

    def random_neighbor__(self):
        """Given a solution generates a neighbor by applying insertion."""
        rc_index1, rc_index2 = int(random() * len(self.order)), int(random() * len(self.order))
        resulting_cities = self.order.copy()
        city_to_move = resulting_cities[rc_index1]
        resulting_cities.remove(city_to_move)
        resulting_cities.insert(rc_index2, city_to_move)
        return Solution(self.problem, resulting_cities)

    def serialize(self, out):
        """Given a solution write out the traversal of the cities at the given file."""
        print("Visiting cities in order of: ", file=out)
        for city in self.order:
            print(city.location.x, city.location.y, city.process_time, file=out)

    def visualize_convexal_as_svg(self, config: VisualizationConfig) -> SVGGraphic:
        out = SVGGraphic(config.size, config.size)
        out.draw_rect(0, 0, config.size, config.size, 0, "rgb(255, 255, 255)")

        def _rescale(x):
            return  x / self.grid_side_length * config.size
        convexals = self.problem.convexal_cities()
        print(convexals)
        print(len(convexals))
        for c in self.problem.cities:
            if c in convexals:
                out.draw_circle(_rescale(c.location.x), _rescale(
                    c.location.y), 3, 0, config.convexal_city_color)
            else:
                out.draw_circle(_rescale(c.location.x), _rescale(
                    c.location.y), 3, 0, config.city_color)
        k = 0
        cities = self.order.copy()
        cities.insert(0, City(Point(0, 0), 0))
        cities.append(City(Point(0, 0), 0))
        while k < len(cities) - 1:
            out.draw_line(_rescale(cities[k].location.x), _rescale(
                cities[k].location.y), _rescale(cities[k + 1].location.x), _rescale(
                    cities[k + 1].location.y))
            if k == 1:
                out.write_text(_rescale(cities[k].location.x), _rescale(
                    cities[k].location.y), k, font_size="medium")
            k += 1
        return out