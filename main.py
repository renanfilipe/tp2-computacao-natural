import pandas as pd

FILE_NAME = "data/graph2.txt"
ANTS = 10
DECAY = 0.1
ITERATIONS = 2
ALPHA = 0.1
BETA = 0.1


def build_graph() -> tuple:
    df = pd.read_csv(FILE_NAME, sep="\t", names=["from", "to", "weight"])
    graph = dict()
    for _, row in df.iterrows():
        try:
            graph[row["from"]].update({
                row["to"]: {
                    "weight": row["weight"],
                    "pheromone": row["weight"]
                }
            })
        except KeyError as e:
            graph[e.args[0]] = {
                row["to"]: {
                    "weight": row["weight"],
                    "pheromone": row["weight"]
                }
            }
    return graph, len(graph), len(df)


def build_solution(ant: dict, graph: dict, destination: int, starting_node = 1):
    current_node = starting_node
    while current_node != destination:
        possible_nodes = get_possible_nodes(ant["path"], graph[current_node])


def get_possible_nodes(path: list, node: dict) -> list:
    available_nodes = node.keys()
    result = {}
    # result = {node: probability}
    for item in available_nodes:
        if item not in path:
            result.update({item: None})
    total_pheromone = sum([node[x]["weight"]*node[x]["pheromone"] for x in result])
    for item in result:
        result[item] = (node[item]["weight"] * node[item]["pheromone"])/total_pheromone
    return result


def main():
    graph, max_nodes, max_edges = build_graph()
    ants = [{"path": [], "fitness": None}] * ANTS
    t = 1
    while t < ITERATIONS:
        for ant in ants:
            build_solution(ant, graph, max_nodes, 1)
    print()


main()
