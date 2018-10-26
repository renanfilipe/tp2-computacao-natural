import pandas as pd
from not_random import NotRandom
import time

start_time = time.time()

FILE_NAME = "data/graph2.txt"

ANTS = 500
ITERATIONS = 3000
DECAY = 0.05
ALPHA = 1.5
BETA = 0.7
N_BESTS = 1

MAX_MIN_RULE = True
MIN_PHEROMONE = 0.8
MAX_PHEROMONE = 1.5

random = NotRandom()


def build_graph() -> tuple:
    df = pd.read_csv(FILE_NAME, sep="\t")
    graph = dict()
    for row in df.itertuples(index=False):
        # row = ["from", "to, "weight"]
        if row[0] in graph:
            graph[row[0]].update({
                row[1]: {"weight": row[2]}
            })
        else:
            graph[row[0]] = {
                row[1]: {"weight": row[2]}
            }
        if MAX_MIN_RULE:
            graph[row[0]][row[1]]["pheromone"] = row[2] * MAX_PHEROMONE
        else:
            graph[row[0]][row[1]]["pheromone"] = 1.0
    return graph, len(graph)


def build_solution(graph: dict, destination: int, starting_node=1) -> dict:
    current_node = starting_node
    ant = {"path": [starting_node], "fitness": 0, "valid_solution": False}
    while current_node != destination:
        possible_nodes = get_possible_nodes(ant["path"], graph[current_node])
        if not possible_nodes:
            break
        next_node = random.choice(
            a=[*possible_nodes.keys()],
            p=[*possible_nodes.values()]
        )
        ant["path"].append(next_node)
        ant["fitness"] += graph[current_node][next_node]["weight"]
        current_node = next_node
    if ant["path"][-1] == destination:
        ant["valid_solution"] = True
    return ant


def get_possible_nodes(path: list, node: dict) -> dict:
    result = {}
    # result = {node: probability}
    for item in node:
        if item not in path:
            # pheromone ^ alpha * (1.0 / distance) ^ beta
            probability = node[item]["pheromone"] ** ALPHA * (1.0/node[item]["weight"]) ** BETA
            result.update({item: probability})
    # making the sum of the all probabilities equals to 1
    total_pheromone = sum([result[x] for x in result])
    for item in result:
        result[item] = result[item]/total_pheromone
    return result


def apply_pheromone(graph: dict, ants: list):
    for i in range(N_BESTS):
        if ants[i]["valid_solution"]:
            for j in range(1, len(ants[i]["path"])):
                from_node = ants[i]["path"][j-1]
                to_node = ants[i]["path"][j]
                if MAX_MIN_RULE:
                    graph[from_node][to_node]["pheromone"] = (1 - DECAY) * graph[from_node][to_node]["pheromone"]\
                                                             + (MAX_PHEROMONE - graph[from_node][to_node]["pheromone"])
                    if graph[from_node][to_node]["pheromone"] > (graph[from_node][to_node]["weight"] * MAX_PHEROMONE):
                        graph[from_node][to_node]["pheromone"] = graph[from_node][to_node]["weight"] * MAX_PHEROMONE
                    elif graph[from_node][to_node]["pheromone"] < (graph[from_node][to_node]["weight"] * MIN_PHEROMONE):
                        graph[from_node][to_node]["pheromone"] = graph[from_node][to_node]["weight"] * MIN_PHEROMONE
                else:
                    graph[from_node][to_node]["pheromone"] = \
                        (1 - DECAY) * graph[from_node][to_node]["pheromone"] + 1 / ants[i]["fitness"]


def main():
    # build graph from file
    graph, max_nodes = build_graph()
    t = 1
    best_solution = {"fitness": 0}
    while t < ITERATIONS:
        # reset ants path and its fitness
        ants = []
        for _ in range(ANTS):
            # build a valid path
            ants.append(build_solution(graph, max_nodes, 1))

        # sort the ants by the highest fitness
        ants = sorted(ants, key=lambda k: k['fitness'], reverse=True)

        # update the best solution
        if ants[0]["fitness"] > best_solution["fitness"]:
            best_solution = ants[0]

        # apply pheromone and the pheromone decay
        apply_pheromone(graph, ants)
        print(t, "- current best:", ants[0]["fitness"])
        print(t, "- all time best:", best_solution["fitness"])
        t += 1
    print("My program took", time.time() - start_time, "to run")


main()
