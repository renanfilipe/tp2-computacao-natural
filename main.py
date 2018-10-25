import pandas as pd
from not_random import NotRandom

FILE_NAME = "data/graph2.txt"

ANTS = 5000
ITERATIONS = 100
DECAY = 0.05
ALPHA = 1
BETA = 1.1
N_BESTS = 1

MAX_MIN_RULE = True
MIN_PHEROMONE = 0.8
MAX_PHEROMONE = 1.5

random = NotRandom()


def build_graph() -> tuple:
    df = pd.read_csv(FILE_NAME, sep="\t", names=["from", "to", "weight"])
    graph = dict()
    for _, row in df.iterrows():
        try:
            graph[row["from"]].update({
                row["to"]: {
                    "weight": row["weight"],
                    "pheromone": 1.0
                }
            })
        except KeyError as e:
            graph[e.args[0]] = {
                row["to"]: {
                    "weight": row["weight"],
                    "pheromone": 1.0
                }
            }
    return graph, len(graph), len(df)


def build_solution(ant: dict, graph: dict, destination: int, starting_node=1):
    current_node = starting_node
    ant["path"].append(starting_node)
    while current_node != destination:
        possible_nodes = get_possible_nodes(ant["path"], graph[current_node])
        if not possible_nodes:
            break
        next_node = random.choice(
            a=list(possible_nodes.keys()),
            p=list(possible_nodes.values())
        )
        ant["path"].append(next_node)
        ant["fitness"] += graph[current_node][next_node]["weight"]
        current_node = next_node
    if ant["path"][0] == starting_node and ant["path"][-1] == destination:
        ant["valid_solution"] = True


def get_possible_nodes(path: list, node: dict) -> dict:
    available_nodes = node.keys()
    result = {}
    # result = {node: probability}
    for item in available_nodes:
        if item not in path:
            # pheromone ^ alpha * (1.0 / distance) ^ beta
            probability = (node[item]["pheromone"] ** ALPHA) * ((1.0/node[item]["weight"]) ** BETA)
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
                # graph[from_node][to_node]["pheromone"] += 1/graph[from_node][to_node]["weight"]
                graph[from_node][to_node]["pheromone"] += 1/ants[i]["fitness"]
            for node in graph:
                for item in graph[node]:
                    graph[node][item]["pheromone"] *= (1 - DECAY)
                    if MAX_MIN_RULE:
                        if graph[node][item]["pheromone"] > (graph[node][item]["weight"] * MAX_PHEROMONE):
                            graph[node][item]["pheromone"] = graph[node][item]["weight"] * MAX_PHEROMONE
                        elif graph[node][item]["pheromone"] < (graph[node][item]["weight"] * MIN_PHEROMONE):
                            graph[node][item]["pheromone"] = graph[node][item]["weight"] * MIN_PHEROMONE

def main():
    # build graph from file
    graph, max_nodes, max_edges = build_graph()
    t = 1
    best_solution = {"fitness": 0}
    while t < ITERATIONS:
        # reset ants path and its fitness
        ants = []
        for _ in range(ANTS):
            ants.append({"path": [], "fitness": 0, "valid_solution": False})

        # build a valid path
        for ant in ants:
            build_solution(ant, graph, max_nodes, 1)

        # sort the ants by the highest fitness
        ants = sorted(ants, key=lambda k: k['fitness'], reverse=True)

        # update the best solution
        best_solution = ants[0] if ants[0]["fitness"] > best_solution["fitness"] else best_solution

        # apply pheromone and the pheromone decay
        apply_pheromone(graph, ants)
        print(t, "- current best:", ants[0]["fitness"])
        print(t, "- all time best:", best_solution["fitness"])
        t += 1
    print()

main()
