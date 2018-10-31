import pandas as pd
import numpy as np
# from not_random import NotRandom
import timeit
import json
import multiprocessing as mp

FILE_NAME = "data/graph2.txt"

ANTS = 0
ITERATIONS = 10
DECAY = 0.05
ALPHA = 1.5
BETA = 0.7
N_BESTS = 1

MIN_PHEROMONE = 0.8
MAX_PHEROMONE = 1.5

random = np.random


def build_graph() -> tuple:
    df = pd.read_csv(FILE_NAME, sep="\t")
    graph = dict()
    # row = ["from", "to, "distance"]
    for row in df.itertuples(index=False):
        try:
            graph[row[0]].update({row[1]: {"distance": row[2], "pheromone": row[2] * MAX_PHEROMONE}})
        except KeyError:
            graph[row[0]] = {row[1]: {"distance": row[2], "pheromone": row[2] * MAX_PHEROMONE}}
    return graph, len(graph), len(df)


def build_solution(graph: dict, destination: int) -> dict:
    current_node = 1
    ant = {"path": [1], "fitness": 0}
    while current_node != destination:
        possible_nodes = get_possible_nodes(ant["path"], graph[current_node])
        try:
            next_node = random.choice(a=[*possible_nodes.keys()], p=[*possible_nodes.values()])
            ant["path"].append(next_node)
            ant["fitness"] += graph[current_node][next_node]["distance"]
            current_node = next_node
        except ValueError:
            break
    # invalid paths will have their fitness value set to 0
    if ant["path"][-1] != destination:
        ant["fitness"] = 0
    return ant


def get_possible_nodes(path: list, node: dict) -> dict:
    # result = {node: probability}
    result = {}
    # dic used to speed up the process of checking if a key is in the list, try and except are faster than ifs
    dict_list = {item: None for item in path}
    for item in node:
        try:
            dict_list[item]
        except KeyError:
            # pheromone ^ alpha * (1.0 / distance) ^ beta
            result.update({item: node[item]["pheromone"] ** ALPHA * (1.0/node[item]["distance"]) ** BETA})
    # making the sum of the all probabilities equals to 1
    total_p = sum([result[x] for x in result])
    for item in result:
        result[item] = result[item]/total_p
    return result


def apply_pheromone(graph: dict, ant: dict):
    for j in range(1, len(ant["path"])):
        node = graph[ant["path"][j-1]][ant["path"][j]]
        node["pheromone"] = (1 - DECAY) * node["pheromone"] + MAX_PHEROMONE - node["pheromone"]
        node["pheromone"] = max(node["distance"] * MIN_PHEROMONE, min(node["distance"] * MAX_PHEROMONE, node["pheromone"]))


def start():
    # build graph from file
    global ANTS
    solutions = {}
    for i in range(1):
        plot_solution = []
        graph, max_nodes, max_edges = build_graph()
        ANTS = max_edges
        best_solution = {"fitness": 0}
        for t in range(ITERATIONS):
            # create a list of ants with its path and its fitness. the list is sorted by the highest fitness
            ants = sorted([build_solution(graph, max_nodes) for _ in range(ANTS)], key=lambda k: k["fitness"], reverse=True)
            # update the best solution
            best_solution = max(ants[0], best_solution, key=lambda k: k["fitness"])
            # apply pheromone and the pheromone's decay
            apply_pheromone(graph, ants[0])
            plot_solution.append(best_solution["fitness"])
            print("%d: %d all time best: %d" % (i, t, best_solution["fitness"]))
        # print("%d all time best: %d" % (i, best_solution["fitness"]))
        solutions.update({i: plot_solution})
    with open('graph1_ants_edges-ite_1000-decay_005-alp_15-beta_07-minphe_08-maxphe_15.json', 'w') as outfile:
        json.dump(solutions, outfile)
    print()

# start()
print(timeit.timeit(setup = 'from main import start', stmt = 'start()', number = 10))
