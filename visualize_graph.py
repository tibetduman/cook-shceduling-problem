import argparse
from pathlib import Path
import matplotlib.pyplot as plt

def graph(mod_num, iter_num, graph_points):
    iterations = []
    penalties = []
    best_scores = []
    for one_data in graph_points:
        iterations.append(float(one_data[0]))
        penalties.append(float(one_data[1]))
        best_scores.append(float(one_data[2]))

    plt.plot(iterations, penalties)
    plt.plot(iterations, best_scores)
    plt.xlabel('iterations')
    plt.ylabel('penalty')
    plt.title('penalty over time for % {}, {}k iterations'.format(mod_num, iter_num))
    plt.savefig("research_mod_{}_for_{}k.png".format(mod_num, iter_num))
