"""The script to generate random examples for the SDTSP."""
from pathlib import Path
from city import City
from point import Point
from random import random
from problem import Problem
import os

CITY_NUM = 100
WIDTH = 20
HEIGHT = 30
PROBLEM_NUM = 10
PROBLEM_TYPE = "large"
def generate_and_write_random_problem(file_name):
    """Generates and writes the problem description to the file."""
    cities = []
    for i in range(CITY_NUM):
        rand_x, rand_y, rand_p = WIDTH * random(), HEIGHT * random(), 2 + 2 * random()
        cities.append(City(Point(rand_x, rand_y), rand_p))
    problem = Problem(cities)
    problem.serialize(Path(file_name).open("w"))

def generate_n_many_problems(n):
    os.mkdir("problems/" + PROBLEM_TYPE)
    for i in range(n):
        generate_and_write_random_problem("problems/" + PROBLEM_TYPE + "/" + PROBLEM_TYPE + str(i) + ".txt")

generate_n_many_problems(PROBLEM_NUM)
print("Successfully generated {3} problems for a grid with {0}cm height, {1}cm width, with {2} cities".format(HEIGHT, WIDTH, CITY_NUM, PROBLEM_NUM))
