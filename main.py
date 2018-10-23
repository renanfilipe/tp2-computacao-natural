import pandas as pd

FILE_NAME = "data/graph2.txt"


# graph1 = {
#   'a': {'b': 1, 'c':  4},
# }
def build_graph():
    df = pd.read_csv(FILE_NAME, sep="\t", names=["from", "to", "weight"])
    graph = dict()
    for index, row in df.iterrows():
        try:
            graph[row["from"]].update({row["to"]: row["weight"]})
        except KeyError as e:
            graph[e.args[0]] = {row["to"]: row["weight"]}
    return graph, len(graph), len(df)


def main():
    graph, max_vertices, max_edges = build_graph()

    print()


main()
