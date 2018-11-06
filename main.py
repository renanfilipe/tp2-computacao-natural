import pandas as pd
import numpy as np
import json

# nome do arquivo de entrada
FILE_NAME = "graph2.txt"

# hiperparametros
# eles estao no formato de lista para que varios testes fossem realizados em uma unica execucao
ANTS = [100, 190, 500, 1000]
ITERATIONS = [30, 100, 300, 1000]
DECAY = [0.05, 0.15, 0.3]
ALPHA = 1.5
BETA = 0.5
N_TESTS = 10
MIN_PHEROMONE = 0.0
MAX_PHEROMONE = 1.0

random = np.random


# le os dados do arquivo de entrada e controi o grafo a partir destes dados
# retorna: grafo, numero de vertices, numero de arestas
def build_graph() -> tuple:
    df = pd.read_csv("data/" + FILE_NAME, sep="\t", names=[0, 1, 2])
    # faz com que o intervalo das distancias fique entre 0 e 1
    df[2] = df[2] / 10
    graph = dict()
    # loop em todas as linhas do dataframe
    # row = ["do vertice", "para o vertice", "distancia"]
    for row in df.itertuples(index=False):
        # try e except foram usados por serem mais baratos computacionalmente do que ifs em python
        try:
            # feromonios sao inicializados no valor maximo
            graph[row[0]].update({row[1]: {"distance": row[2], "pheromone": MAX_PHEROMONE}})
        except KeyError:
            # feromonios sao inicializados no valor maximo
            graph[row[0]] = {row[1]: {"distance": row[2], "pheromone": MAX_PHEROMONE}}
    return graph, len(graph), len(df)


# constroi uma solucao
# recebe: grafo e o vertice destino
# retorna: formiga
def build_solution(graph: dict, destination: int) -> dict:
    current_node = 1
    # todas formigas iniciam no vertice 1 do grafo
    ant = {"path": [1], "fitness": 0}
    # executa enquanto nao chegar no destino
    while current_node != destination:
        # pega a lista com os possiveis nos a serem visitados
        possible_nodes = get_possible_nodes(ant["path"], graph[current_node])
        # try except para o caso de nao haver vertices ainda nao visitados, o que faz com que a lista seja vazia
        try:
            # seleciona aleatoriamente um vertice
            next_node = random.choice(a=[*possible_nodes.keys()], p=[*possible_nodes.values()])
            # adiciona vertice na lista de vertices visitados
            ant["path"].append(next_node)
            # incrementa fitness com a distancia percorrido para o vertice atual
            ant["fitness"] += graph[current_node][next_node]["distance"]
            current_node = next_node
        except ValueError:
            break
    # caminhos invalidos terao suas fitness zeradas
    if ant["path"][-1] != destination:
        ant["fitness"] = 0
    else:
        # caso o caminho seja valido o valor da fitness sera multiplicado por 10 para que esse retorne a escala original
        ant["fitness"] *= 10
    return ant


# recebe: o caminho visitado ate o momento e um dicionario que contem os possiveis vertices que podem ser visitados
# retorna: lista de possiveis vertices a serem visitados juntamente com a chance de cada um ser visitado
def get_possible_nodes(path: list, node: dict) -> dict:
    # result = {vertice: probabilidade de ser visitado}
    result = {}
    # loop para cada vertice ainda nao visitado
    for item in set(node.keys()).difference(path):
        # calcula a regra de transicao
        result.update({item: node[item]["pheromone"] ** ALPHA * (1.0 / node[item]["distance"]) ** BETA})

    # normaliza a regra de transicao, para que a soma das probabilidades seja igual a 1
    total_p = sum([result[x] for x in result])
    for item in result:
        result[item] = result[item]/total_p
    return result


# aplica o feromonio ao caminho percorrido pela formiga
# recebe: grafo, formiga, taxa de evaporacao
def apply_pheromone(graph: dict, ant: dict, decay: float):
    # loop que percorre todos vertices visitados pela formiga
    for j in range(1, len(ant["path"])):
        node = graph[ant["path"][j-1]][ant["path"][j]]
        # calcula novo valor do feromonio
        node["pheromone"] = (1 - decay) * node["pheromone"] + MAX_PHEROMONE - node["pheromone"]
        # faz que com o novo valor do feromonio fique no intervalo definido pela estrategia MAX-MIN
        node["pheromone"] = max(node["distance"] * MIN_PHEROMONE, min(node["distance"] * MAX_PHEROMONE, node["pheromone"]))


def start():
    for ants in ANTS:
        for iterations in ITERATIONS:
            for decay in DECAY:
                results = {}
                for n_tests in range(N_TESTS):
                    plot_solution = []
                    # constroi grafo a partir do arquivo
                    graph, max_nodes, max_edges = build_graph()
                    best_solution = {"fitness": 0}
                    for t in range(iterations):
                        # cria uma lista ordenada de formigas pela maior fitness
                        solutions = sorted([build_solution(graph, max_nodes) for _ in range(ants)], key=lambda k: k["fitness"], reverse=True)
                        # atualiza a melhor solucao
                        best_solution = max(solutions[0], best_solution, key=lambda k: k["fitness"])
                        # aplica feromonio no grafo, juntamente com a taxa de evaporacao
                        apply_pheromone(graph, solutions[0], decay)
                        plot_solution.append(best_solution["fitness"])
                    results.update({n_tests: plot_solution})
                # salva resultado no formato json para futura analise
                with open('%s_ants_%d-ite_%d-decay_%s.json' % (FILE_NAME, ants, iterations, str(decay)), 'w') as outfile:
                    json.dump(results, outfile)

start()
