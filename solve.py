"""Solves the given input problem"""
from copy import copy
from pathlib import Path
from random import random
import sys
import os
from time import time

from city import City
from problem import Problem
from solution import Solution
import math
from point import Point
import visualize_graph
import visualize

### Helper functions to read and write to files.
def infile(file):
    return Path(file).open("r")

def outfile(file):
    return Path(file).open("w")

def random_solver(problem: Problem)->Solution:
    """Randomly visits each city."""
    cities_to_visit = problem.cities.copy()
    order = []
    while cities_to_visit:
        visiting = cities_to_visit[int(random() * len(cities_to_visit))]
        order.append(visiting)
        cities_to_visit.remove(visiting)
    return Solution(problem, order)

def in_order_solver(problem: Problem)-> Solution:
    """Visits each city in the order of problem input."""
    return Solution(problem, problem.cities)

def nearest_neighbor_solver(problem: Problem)-> Solution:
    """Greedily visits the closest city."""
    cities_to_visit = problem.cities.copy()
    order = []
    origin = City(Point(0, 0), 0)
    while cities_to_visit:
        if len(order) == 0:
            visiting = origin.closest_city(cities_to_visit)
            order.append(visiting)
        else:
            visiting = order[-1].closest_city(cities_to_visit)
            order.append(visiting)
        cities_to_visit.remove(visiting)
    return Solution(problem, order)

def greedy_highest_process_time_solver(problem: Problem)->Solution:
    """Greedily visits the city with the next highest process time."""
    return Solution(problem, sorted(problem.cities, key=lambda c: c.process_time))

def convexhull_solver(problem: Problem)->Solution:
    """Given a problem solves it by finding the convexhull of the points and then inserting in the rest."""
    inserted_cities = problem.convexal_cities()
    cities_to_insert = []
    for city in problem.cities:
        if city not in inserted_cities:
            cities_to_insert.append(city)
    while cities_to_insert:
        current_cost = in_order_solver(Problem(inserted_cities)).cost
        best_city = None
        best_insertion_cost = float('inf')
        insertion_index = 0
        for city in cities_to_insert:
            for i in range(1, len(inserted_cities)):
                copy_of_cities = inserted_cities.copy()
                copy_of_cities.insert(i, city)
                cost_of_insertion = Solution(problem, copy_of_cities).cost - current_cost
                if cost_of_insertion < best_insertion_cost:
                    best_city = city
                    best_insertion_cost = cost_of_insertion
                    insertion_index = i
        inserted_cities.insert(insertion_index, best_city)
        cities_to_insert.remove(best_city)
    inserted_cities.remove(City(Point(0, 0), 0))
    return Solution(problem, inserted_cities)

def convexhull_oropt_solver(problem: Problem)-> Solution:
    sol = convexhull_solver(problem)
    print("Convexhull solution before oropt has cost: ", sol.cost)
    return or_opt(sol)

def or_opt(sol: Solution)->Solution:
    """Given a solution applies OR-OPT to improve the solution."""
    k_consecutive = 3
    while k_consecutive > 0:
        idx = 0
        while idx <= len(sol.order) - k_consecutive:
            insertion_idx = idx + k_consecutive
            cities_to_insert = sol.order[idx: idx + k_consecutive]
            reversed_cities_to_insert = cities_to_insert.copy()
            reversed_cities_to_insert.reverse()
            while insertion_idx < len(sol.order):
                new_order = sol.order[:idx] + sol.order[idx + k_consecutive: insertion_idx] + cities_to_insert + sol.order[insertion_idx:]
                new_reversed_order = sol.order[:idx] + sol.order[idx + k_consecutive: insertion_idx] + reversed_cities_to_insert + sol.order[insertion_idx:]
                in_order_inserted_solution = Solution(sol.problem, new_order)
                reversed_inserted_solution = Solution(sol.problem, new_reversed_order)
                if in_order_inserted_solution.cost < sol.cost:
                    print("switching to better when k is", k_consecutive)
                    sol = in_order_inserted_solution
                    idx += k_consecutive
                    break
                if reversed_inserted_solution.cost < sol.cost:
                    print("switching to better when k is", k_consecutive)
                    sol = reversed_inserted_solution
                    idx += k_consecutive
                    break
                insertion_idx += 1
            idx += 1
        k_consecutive -= 1
    return sol

def hill_climbing_solver(problem: Problem)-> Solution:
    """Given a problem applies hill climbing to it."""
    current_solution = random_solver(problem)
    current_cost = current_solution.cost
    N, n = 10000, 0
    while n < N:
        if n % 500 == 0:
            print(current_cost)
        new_solution = current_solution.random_neighbor()
        new_cost = new_solution.cost
        if new_cost < current_cost:
            current_solution = new_solution
            current_cost = new_cost
        n += 1
    return current_solution

def simulated_annealing_solver(problem: Problem)-> Solution:
    """Applies simulated annealing to a random starting solution."""
    current_solution = random_solver(problem)
    current_cost = current_solution.cost
    print("Starting random solution cost is: ", current_cost)
    graph_points = []
    best_solution = current_solution
    best_cost = current_cost
    mod_num = 10
    alpha = 0.995
    T = 6.63
    N, n = 48000, 0
    while n < N:
        next_solution = current_solution.random_neighbor()
        new_cost = next_solution.cost
        delta = current_cost - new_cost
        if delta >= 0:
            current_solution, current_cost = next_solution, new_cost
            if new_cost < best_cost:
                best_solution = current_solution
                best_cost = new_cost
        else:
            if random() < (math.e ** (delta/T)):
                current_solution, current_cost = next_solution, new_cost
                if new_cost < best_cost:
                    best_solution = current_solution
                    best_cost = new_cost
        n += 1
        if n % mod_num == 0:
            T *= alpha
        if n % 1000 == 0:
            graph_points.append((n, current_cost, best_cost))
        #"""
        if n == (N * 0.9) and best_cost < current_cost:
            print("Switching from {0} cost solution to better solution with {1} cost".format(current_cost, best_cost))
            current_solution = best_solution
        #"""
    visualize_graph.graph(mod_num, N, graph_points)
    return min(current_solution, best_solution, key=lambda x: x.cost)

def mbo_solver_one_step_sharing(problem: Problem)->Solution:
    """Apply Migrating Birds Optimization with a single layer of sharing to the given problem."""
    n, k, x = 501, 11, 1 # Number of birds, neighbors, and neighbors to share
    i = 0 # Iteration number
    J = 1
    I = 1000000 / n  / J# Number of leader changes
    leader = random_solver(problem)
    left_tail = [random_solver(problem) for i in range((n - 1) // 2)]
    right_tail = [random_solver(problem) for i in range((n - 1) // 2)]
    while i < I:
        j = 0
        while j < J:
            leader, solutions_to_share = mbo_update_leader(leader, k, x)
            left_tail = single_step_immediate_calculation_tail_processing(left_tail, solutions_to_share[0], k, x)
            right_tail = single_step_immediate_calculation_tail_processing(right_tail, solutions_to_share[1], k, x)
            j += 1
        if i % 2 == 0:
            new_leader = left_tail[0]
            left_tail.remove(new_leader)
            left_tail.append(leader)
        else:
            new_leader = right_tail[0]
            right_tail.remove(new_leader)
            right_tail.append(leader)
        leader = new_leader
        i += 1
    all_birds = [leader] + left_tail + right_tail
    print("Minimum is {0}, maximum is {1}, and the average is {2}".format(min(all_birds, key=lambda b: b.cost).cost,
     max(all_birds, key=lambda b: b.cost).cost, average_of_solutions(all_birds)))
    return min(all_birds, key=lambda b: b.cost)


def mbo_solver_multiple_step_sharing(problem: Problem)->Solution:
    """Apply Migrating Birds Optimization with a multiple layer of sharing to the given problem."""
    n, k, x = 21, 7, 1 # Number of birds, neighbors, and neighbors to share
    i = 0 # Iteration number
    J = 1 # number of wing flaps before leader change
    I = 8000 / n / J # Number of leader changes
    leader = random_solver(problem)
    left_tail = [random_solver(problem) for i in range((n - 1) // 2)]
    right_tail = [random_solver(problem) for i in range((n - 1) // 2)]
    while i < I:
        j = 0
        while j < J:
            leader, solutions_to_share = mbo_update_leader(leader, k, x)
            left_tail = multiple_step_immediate_calculation_tail_processing(left_tail, solutions_to_share[0], k, x)
            right_tail = multiple_step_immediate_calculation_tail_processing(right_tail, solutions_to_share[1], k, x)
            j += 1
        if i % 2 == 0:
            new_leader = left_tail[0]
            left_tail.remove(new_leader)
            left_tail.append(leader)
        else:
            new_leader = right_tail[0]
            right_tail.remove(new_leader)
            right_tail.append(leader)
        leader = new_leader
        i += 1
    all_birds = [leader] + left_tail + right_tail
    print("Minimum is {0}, maximum is {1}, and the average is {2}".format(min(all_birds, key=lambda b: b.cost).cost,
     max(all_birds, key=lambda b: b.cost).cost, average_of_solutions(all_birds)))
    return min(all_birds, key=lambda b: b.cost)

def mbo_update_leader(leader: Solution, k: int, x: int):
    """Given the leader bird in mbo optimization updates the leader and returns the solutions to share with the other birds."""
    leader_improvements = [leader.random_neighbor() for i in range(k)]
    leader_improvements.sort(key=lambda x: x.cost)
    if leader_improvements[0].cost < leader.cost:
        leader = leader_improvements[0]
        solutions_to_share = leader_improvements[1:3]
    else:
        solutions_to_share = leader_improvements[:2]
    return leader, solutions_to_share

def single_step_tail_processing(tail, original_solutions_to_share, k, x):
    """Given a tail (a list of birds) and original solutions to share applies mbo single step to the birds in the tail."""
    solution_to_share = copy(original_solutions_to_share)
    updated_tail = []
    for bird in tail:
        bird_improvements = [bird.random_neighbor() for i in range(k - x)]
        bird_improvements.sort(key=lambda x: x.cost)
        if bird_improvements[0].cost < bird.cost:
            updated_tail.append(bird_improvements[0])
            solution_to_share = bird_improvements[1]
        else:
            if solution_to_share.cost < bird.cost:
                updated_tail.append(copy(solution_to_share))
            else:
                updated_tail.append(bird)
            solution_to_share = bird_improvements[0]
    return updated_tail

def multiple_step_tail_processing(tail, original_solution_to_share, k, x):
    """Given a tail (a list of birds) and original solutions to share applies mbo multiple step to the birds in the tail."""
    solution_to_share = copy(original_solution_to_share)
    updated_tail = []
    for bird in tail:
        bird_improvements = [bird.random_neighbor() for i in range(k - x)]
        bird_improvements.sort(key=lambda x: x.cost)
        if bird_improvements[0].cost < bird.cost:
            updated_tail.append(bird_improvements[0])
            solution_to_share = min(solution_to_share, bird_improvements[1], key=lambda x: x.cost)
        else:
            if solution_to_share.cost < bird.cost:
                updated_tail.append(copy(solution_to_share))
                solution_to_share = bird_improvements[0]
            else:
                updated_tail.append(bird)
                solution_to_share = min(solution_to_share, bird_improvements[0], key=lambda x: x.cost)
    return updated_tail

def single_step_immediate_calculation_tail_processing(tail, original_solutions_to_share, k, x):
    """Given a tail (a list of birds) and original solutions to share applies mbo single step immediate calculation to the birds in the tail."""
    solution_to_share = copy(original_solutions_to_share)
    updated_tail = []
    for bird in tail:
        bird_improvements = [bird.random_neighbor() for i in range(k - x)]
        bird_improvements.append(solution_to_share)
        bird_improvements.sort(key=lambda x: x.cost)
        if bird_improvements[0].cost < bird.cost:
            updated_tail.append(bird_improvements[0])
        else:
            updated_tail.append(bird)
        i = 0
        while bird_improvements[i] is solution_to_share or bird_improvements[i] is updated_tail[-1]:
            i += 1
        solution_to_share = bird_improvements[i]
    return updated_tail

def multiple_step_immediate_calculation_tail_processing(tail, original_solutions_to_share, k, x):
    """Given a tail (a list of birds) and original solutions to share applies mbo multiple step immediate calculation to the birds in the tail."""
    solution_to_share = copy(original_solutions_to_share)
    updated_tail = []
    for bird in tail:
        bird_improvements = [bird.random_neighbor() for i in range(k - x)]
        bird_improvements.append(solution_to_share)
        bird_improvements.sort(key=lambda x: x.cost)
        if bird_improvements[0].cost < bird.cost:
            updated_tail.append(bird_improvements[0])
            solution_to_share = bird_improvements[1]
        else:
            updated_tail.append(bird)
            solution_to_share = bird_improvements[0]
    return updated_tail

def average_of_solutions(solutions)->float:
    """Given a list of solutions returns the average cost of them."""
    total = 0
    for sol in solutions:
        total += sol.cost
    return total / len(solutions)

def main():
    args = sys.argv[1:]
    if len(args) == 2:
        with infile(args[0]) as f:
            problem = Problem.parse(f.readlines())
            starting_time = time()
            solution = simulated_annealing_solver(problem)
            ending_time = time()
            print("it took {0} seconds to solve".format(round(ending_time - starting_time, 5)))
            assert(solution.valid())
            print("Found a solution with cost: ", solution.cost)
            with outfile(args[1]) as g:
                print("# Penalty: ", solution.cost, file=g)
            svg = solution.visualize_convexal_as_svg(visualize.VisualizationConfig())
            with Path("visual.svg").open("w") as f:
                f.write(str(svg))
    else:
        # in this case solve all problems in problems directory (speed tunning)
        directory_name = "problems/" + args[0] + "/"
        all_problems = os.listdir(directory_name)
        all_problems.sort()
        solver_name = "solutions/" + args[0] + "/sa_mi/"
        averages = []
        k = 0
        while k < 10:
            problem = all_problems[k]
            with infile(directory_name + problem) as f:
                p = Problem.parse(f.readlines())
                costs = []
                best_solution = None
                best_cost = float('inf')
                worst_cost = 0
                for i in range(10):
                    solution = simulated_annealing_solver(p)
                    assert(solution.valid())
                    current_cost = solution.cost
                    costs.append(current_cost)
                    if current_cost < best_cost:
                        best_solution = solution
                        best_cost = current_cost
                    worst_cost = max(worst_cost, current_cost)
                with Path(solver_name + problem).open("w") as l:
                    best_solution.serialize(l)
                average = round(sum(costs) / len(costs), 3)
                averages.append(average)
                with Path(solver_name + "all_solutions.txt").open("a") as g:
                    g.write(problem + " solved with simulated annealing more iterations has the cost of min {0}, max {1}, and average {2} \n ".format(best_cost, worst_cost, average))
            k += 1
        print("average of 10 problems is ", sum(averages) / len(averages))
if __name__ == "__main__":
    main()