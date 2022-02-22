from typing import Dict
from collections import Counter
import sys

import networkx as nx
import matplotlib.pyplot as plt


class EDA:
    def __init__(self, G):
        if isinstance(G, dict):
            self.G = nx.DiGraph(G)
        else:
            self.G = G

    def degree_count(self, total=False, in_degree=False, out_degree=False):
        """
        count each node degree
        :param total: in_degree + out_degree
        :param in_degree:
        :param out_degree:
        :return:
        """
        if total:
            return sorted([self.G.degree(n) for n in self.G.nodes()])
        elif in_degree:
            return sorted([self.G.in_degree(n) for n in self.G.nodes()])
        elif out_degree:
            return sorted([self.G.out_degree(n) for n in self.G.nodes()])
        else:
            print('Not Choose Option')
            return None

    def plot_node_degree(self):
        """
        Plot a list of frequency of each degree value.
        :return:
        """
        total_edges = self.G.number_of_edges()
        print(total_edges)
        degrees = self.degree_count(total=True)
        in_degrees = self.degree_count(in_degree=True)
        out_degrees = self.degree_count(out_degree=True)

        degree_counts = Counter(degrees)
        in_degree_counts = Counter(in_degrees)
        out_degree_counts = Counter(out_degrees)

        x, y = zip(*degree_counts.items())
        in_x, in_y = zip(*in_degree_counts.items())
        out_x, out_y = zip(*out_degree_counts.items())

        plt.figure(1)

        # prep axes
        plt.xlabel('degree')
        plt.xscale('log')
        plt.xlim(1, max(x))

        plt.ylabel('frequency')
        plt.yscale('log')
        plt.ylim(1, max(y))

        plt.plot(x, y, marker='.', label='Total Degrees')
        plt.plot(in_x, in_y, marker='.', label='Total In Degrees')
        plt.plot(out_x, out_y, marker='.', label='Total Out Degrees')
        plt.legend()
        plt.show()

        all_degrees = [v for _, v in nx.degree(self.G)]
        plt.boxplot(all_degrees)
        plt.show()


class NetworkAnalysis:
    """
    네트워크 분석 기법을 이용해 그래프 분석

    군집 계수(Clustering Coefficient), 노드 중심성(Network Centrality) 분석
    """
    def __init__(self, G: nx.DiGraph):
        self.G = G

    def clustering_coefficient(self):
        """
        '그래프가 서로 얼만나 연결되어 있는지'에 대한 군집 계수를 구하는 함수
        :return:
        """
        sys.stdout.write('-- Start Calculate Clustering Coefficient --\n')
        lcc = nx.clustering(self.G)
        average_lcc = nx.average_clustering(self.G)
        sys.stdout.write('--Calculate Clustering Coefficient Done--\n')
        sys.stdout.write('Start Plot Clustering Coefficient\n')
        plt.hist(lcc.values())
        plt.xlabel('Clustering')
        plt.ylabel('Frequency')
        plt.show()
        sys.stdout.write(f'Average Cluster Coefficient" {average_lcc}\n')
        sys.stdout.write('Plot Clustering Done\n\n')

    def network_centrality(self):
        """
        '그래프에서 어떤 노드가 가장 중요한 노드'인지에 노드 중심성을 구하는 함수
        :return:
        """
        sys.stdout.write('start Calculate network centrality\n')
        in_degree_centrality: Dict = nx.in_degree_centrality(self.G)
        out_degree_centrality: Dict = nx.out_degree_centrality(self.G)
        closeness_centrality: Dict = nx.closeness_centrality(self.G)
        betweenness_centrality: Dict = nx.betweenness_centrality(self.G)

        sys.stdout.write('Calculate network centrality Done\n')
        sys.stdout.write('Start plot network centrality\n')
        fig, axes = plt.subplots(2, 2)
        axes[0][0].boxplot(in_degree_centrality.values())
        axes[0][1].boxplot(out_degree_centrality.values())
        axes[1][0].boxplot(closeness_centrality.values())
        axes[1][1].boxplot(betweenness_centrality.values())

        axes[0][0].set_title('in_degree centrality')
        axes[0][1].set_title('out_degree centrality')
        axes[1][0].set_title('closeness_centrality')
        axes[1][1].set_title('betweennes_centrality')

        fig.suptitle('Node Centrality', fontweight='bold')
        plt.show()
        sys.stdout.write('plot network centrality done')
