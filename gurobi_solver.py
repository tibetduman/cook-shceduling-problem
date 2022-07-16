import sys
import os
from time import time
from pathlib import Path
from city import City
from problem import Problem
from solution import Solution
from point import Point
import math

import gurobipy as gp
from gurobipy import GRB

import sys
import math
import random
from itertools import combinations

with Path("problems/large/large9.txt").open("r") as f:
    problem = Problem.parse(f.readlines())
Origin = City(Point(0, 0), 0)
problem.cities.insert(0, Origin)

# Callback - use lazy constraints to eliminate sub-tours
def subtourelim(model, where):
    if where == GRB.Callback.MIPSOL:
        vals = model.cbGetSolution(model._vars)
        # find the shortest cycle in the selected edge list
        tour = subtour(vals)
        if len(tour) < n:
            # add subtour elimination constr. for every pair of cities in tour
            model.cbLazy(gp.quicksum(model._vars[i,j] + model._vars[j,i]
                                for i,j in combinations(tour, 2))
                        <= len(tour)-1)


# Given a tuplelist of edges, find the shortest subtour

def subtour(vals):
    # make a list of edges selected in the solution
    edges = gp.tuplelist((i, j) for i, j in vals.keys()
                         if vals[i, j] > 0.5)
    unvisited = list(range(n))
    cycle = range(n+1)  # initial length has 1 more city
    while unvisited:  # true if list is non-empty
        thiscycle = []
        neighbors = unvisited
        while neighbors:
            current = neighbors[0]
            thiscycle.append(current)
            unvisited.remove(current)
            neighbors = [j for i, j in edges.select(current, '*')
                         if j in unvisited]
        if len(cycle) > len(thiscycle):
            cycle = thiscycle
    return cycle

n = 101

points = [city for city in problem.cities]

# Dictionary of Euclidean distance between each pair of points

dist = {}
for i, source in enumerate(points):
    for j, destination in enumerate(points):
        if i == j:
            continue
        dist[(i, j)] = max(source.distance(destination), source.process_time)


m = gp.Model()
m.Params.TimeLimit = 30
# Create variables

vars = gp.tupledict()
for i,j in dist.keys():
   vars[i,j] = m.addVar(obj=dist[i,j], vtype=GRB.BINARY,
                        name='e[%d,%d]'%(i,j))

# You could use Python looping constructs and m.addVar() to create
# these decision variables instead.  The following would be equivalent
# to the preceding m.addVars() call...
#
# vars = tupledict()
# for i,j in dist.keys():
#   vars[i,j] = m.addVar(obj=dist[i,j], vtype=GRB.BINARY,
#                        name='e[%d,%d]'%(i,j))


# Add degree-2 constraint

m.addConstrs(vars.sum(i,'*') == 1 for i in range(n))
m.addConstrs(vars.sum('*',i) == 1 for i in range(n))

# Using Python looping constructs, the preceding would be...
#
# for i in range(n):
#   m.addConstr(sum(vars[i,j] for j in range(n)) == 2)


# Optimize model
m.setParam('MIPGap', 0)
m._vars = vars
m.Params.LazyConstraints = 1
m.optimize(subtourelim)

vals = m.getAttr('X', vars)
tour = subtour(vals)
assert len(tour) == n

print('')
print('Optimal tour: %s' % str(tour))
print('Optimal cost: %g' % m.ObjVal)
problem.cities.remove(Origin)
order = []
for city_num in tour:
    if city_num == 0:
        continue
    order.append(problem.cities[city_num - 1])
sol = Solution(problem, order)
print(sol.cost)
assert(sol.valid())
print('')
