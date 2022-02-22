import sys
from operator import itemgetter
from typing import Dict, List

import mpld3
from pyvis.network import Network
import plotly.express as px
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from matplotlib import (font_manager,
                        rc,
                        rcParams,
                        matplotlib_fname,
                        get_cachedir,
                        use)
from tqdm import tqdm

from eda import EDA, NetworkAnalysis
from file_manager import FileManager

# if platform.system() == 'Windows':
use('Agg')
print(matplotlib_fname())
print(get_cachedir())
font_path = 'C://Windows//Fonts//NanumGothic.ttf'
font = font_manager.FontProperties(fname=font_path).get_name()
print('font', font)
rc('font', family=font)
rcParams['font.sans-serif'] = [font, 'sans-serif']
rcParams['axes.unicode_minus'] = False
plt.rc('font', family=font)
plt.rcParams['font.family'] = font
plt.rcParams['axes.unicode_minus'] = False
print(plt.rcParams['font.family'])


class GraphModeling:
    def __init__(self) -> None:

    def graph_modeling(self, graph: Dict, direction=True) -> nx.DiGraph:
        sys.stdout.write('<< Convert Dict to Graph >>\n')
        if direction:
            G = nx.DiGraph()
            G.add_nodes_from(graph.keys())
            for idx, (node, edges) in enumerate(tqdm(graph.items())):
                for edge in edges:
                    G.add_edge(node, edge)
        else:
            G = nx.Graph()
            for node, edges in tqdm(graph.items()):
                for edge in edges:
                    G.add_edge(node, edge)

        # Total Numbers of Documents, Nodes, Edges
        sys.stdout.write(f'Total Documents: {len(graph.items())} \n')
        sys.stdout.write(f'Total Nodes: {len(G.nodes)} \n')
        sys.stdout.write(f'Total Edges: {len(G.edges)} \n')
        return G


    def pruning_edges(self, G: nx.DiGraph) -> nx.DiGraph:
        """
        pruning dead_ends node if node in-degree <= 100 and node out-degree == 0
        :param G:
        :return: G: nx.Digraph
        """
        # [TODO] pruning 어떤 기준으로 할지 생각하기

        degrees = [n for n in G.nodes() if G.out_degree(n) == 0 and G.in_degree(n) <= 100]
        n_pruning_edges = sum([G.degree(node) for node in degrees])
        n_dead_node = len(degrees)
        sys.stdout.write(f'Dead Nodes: {n_dead_node}\n')
        sys.stdout.write(f'Pruning Edges: {n_pruning_edges}\n\n')
        G.remove_nodes_from(degrees)
        sys.stdout.write(f'Current Nodes: {G.number_of_nodes()}\n')
        sys.stdout.write(f'Current Edges: {G.number_of_edges()} \n')
        sys.stdout.write(f'Average Degree: {G.number_of_edges()/G.number_of_nodes()}\n')
        return G


def network_analysis(G: nx.DiGraph):
    sys.stdout.write('-- Start network analysis--\n')
    eda = EDA(G)
    eda.plot_node_degree()

    network_eda = NetworkAnalysis(G)
    network_eda.clustering_coefficient()
    network_eda.network_centrality()


def pagerank(G):
    pr_graph: Dict = nx.pagerank(G)
    pr_score: List = sorted(pr_graph.items(), key=itemgetter(1), reverse=True)
    sys.stdout.write(f'pagerank: {pr_score[:100]}')
    return pr_graph


def drawing(G, ax=None):
    pos = nx.kamada_kawai_layout(G)
    plt.title('I.O.I', fontsize=60)
    nx.draw_networkx_nodes(G, pos, node_size=15000, node_color="green", alpha=0.1, ax=ax)
    nx.draw_networkx_edges(G, pos, width=2, edge_color='purple', alpha=0.2, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=25, font_color='black', ax=ax)
    plt.text(fontsize=20, family=font, rotation=0, horizontalalignment='center', verticalalignment='center',
             x=0, y=0, s='pagerank', alpha=0.3, color='purple')


def plot_graph(G):
    # fig, ax = plt.subplots(1, 2, figsize=(50, 25))
    fig = plt.figure(figsize=(50, 25))
    drawing(G)
    # drawing(G, ax[1])
    plt.savefig('pic.png', bbox_inches='tight')
    mpld3.save_html(fig, 'pagerank.html')
    # plt.show()


def test(G):
    df = pd.DataFrame(dict(
        pagerank=nx.pagerank(G),
        degree=nx.eigenvector_centrality(G)
    ))
    t_sne = TSNE(n_components=2, verbose=1, perplexity=40, n_iter=300)
    df = df[:1000]
    # df['pagerank'] = t_sne.fit_transform(df['pagerank'].values.reshape(-1, 1))
    # df['degree'] = t_sne.fit_transform(df['degree'].values.reshape(-1, 1))
    df_test = pd.DataFrame(dict(
        pagerank=df['pagerank'].sort_values(ascending=False),
        degree=df['degree'].sort_values(ascending=False))
    )
    df_test['document'] = df_test.index
    p = px.scatter(df_test, x='pagerank', y='degree', color='pagerank', text='document')
    p.show()


def pyvis_test(G):
    pyvis_network = Network(height=750, width='100%', bgcolor='#222222', font_color='white')
    pyvis_network.barnes_hut()
    pyvis_network.from_nx(G)
    pyvis_network.show('pyvis.html')


def main():
    query: str = 'I.O.I'
    sys.stdout.write('<< Unpickling Graph Data >>\n')
    file_manager = FileManager()
    sys.stdout.write('<< Unpicking done .. >>\n\n')
    graph: Dict = file_manager.load_graph(query=query)
    G = graph_modeling(graph)
    # G = pruning_edges(G)
    # network_analysis(G)
    # pr_graph = pagerank(G)
    # test(G)
    # plot_graph(G)
    # pyvis_test(G)


main()
