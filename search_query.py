import sys
import pickle
import json
from typing import List, Dict, Tuple, Set

from file_manager import FileManager
from linking import Redirect, TreeToGraph


class SearchQuery:
    """
    Query Node가 주어지면 Query와 연결된 Edge들을 지정한 Depth 만큼 찾아주는 클래스.
    이때 Query Node는 Document를 의미하고, Edge는 Document에 속한 Term을 의미한다.
    """
    def __init__(self, graph: Dict, max_depth=1) -> None:
        """

        :param graph: Dict Document와 Term들이 연결되어 있는 딕셔너리 형태의 그래프
        :param max_depth: int Query가 주어졌을 때, 얼마나 깊게 트리를 생성할 것인지
        """
        self.redirect: Redirect = Redirect(dir_path='./data/result/', file_name='redirect.txt')
        self.graph: Dict = graph
        self.max_depth: int = max_depth
        self.nodes: Set = set()
        self.number_of_depth_node: List = [0 for _ in range(self.max_depth+1)]

    def bfs_search_query(self, query: str) -> Dict:
        """
        BFS 기반 level-order 수행을 통해 Query(root node)에 속한 node를 구하는 함수
        큐에 시작 노드를 넣고 BFS를 수행하며, 쿼리와 연결된 문서들을 연결한다.
        최종적으로, Document 이름을 Key로 갖고, Document에 포함된 단어들을[List] Value로 구성된 Dictionary 생성
        => {Document 이름: [단어1, 단어2, ..]}
        :return: 쿼리에 대한 연관된 단어들을 딕셔너리 기반 트리 리턴
        """

        depth: int = 0
        queue: List[Tuple[str, int]] = [(query, depth)]
        query_tree: Dict = {}
        self.number_of_depth_node[0] = 1
        while queue:
            all_edges: Set = set()
            node, cur_depth = queue.pop(0)

            # redirect 있는지 확인
            if node not in self.graph:
                redirect = self.redirect[node]
                node = redirect["redirect"]
                similar_node = redirect["similar"]
                all_edges.update(similar_node)
                self.nodes.update(similar_node)

            if node in self.graph:
                edges = self.graph[node]
                all_edges.update(edges)
                query_tree[node] = list(all_edges)
                for edge in edges:
                    if edge not in self.nodes and cur_depth+1 < self.max_depth:
                        queue.append((edge, cur_depth+1))
                self.number_of_depth_node[cur_depth+1] += len(all_edges)
        self._print_depth_node()
        return query_tree

    def _print_depth_node(self):
        for depth, num in enumerate(self.number_of_depth_node):
            sys.stdout.write(f'depth: {str(depth)} in nodes {str(num)}\n')

        # [TODO] Exception sum(number_of_depth_node) != len(self.nodes)?
        sys.stdout.write(f'total nodes: {str(sum(self.number_of_depth_node))}\n')


def main():
    file_manager = FileManager()
    wiki_graph: Dict = file_manager.load_graph()
    query: str = 'I.O.I'
    search_query = SearchQuery(graph=wiki_graph, max_depth=1)
    query_tree = search_query.bfs_search_query(query)
    file_manager.save_query(query, query_tree, visualize=True)
    tree_to_graph = TreeToGraph(wiki_graph, query)
    query_graph = tree_to_graph.tree_to_graph()
    file_manager.save_query_graph(query, query_graph, visualize=True)


main()
