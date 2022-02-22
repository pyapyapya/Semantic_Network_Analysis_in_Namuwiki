from typing import List, Dict, Set
import os
import pickle
import json

from tqdm import tqdm


class Indexer:
    def __init__(self, dir_path: str, file_name: str) -> None:
        self.dir_path = dir_path
        self.indexer = self._load_indexer(file_name)

    def _load_indexer(self, file_name) -> Dict:
        try:
            indexer = {}
            with open(os.path.join(self.dir_path, file_name), encoding='utf-8') as indexer_file:
                for line in indexer_file.readlines():
                    line = line.split('\t')
                    index_name = line[0]
                    index_location = line[1].strip()
                    indexer[index_name] = index_location
            return indexer
        except Exception as e:
            print(e)
            return {}


class Redirect:
    """
    리다이렉트가 존재하면 최종 링크까지 리다이렉트 시켜 "redirect"에 저장
    리다이렉트할 때, 그 링크의 의미도 분석하기 위해 "similar"에 저장
    """
    def __init__(self, dir_path: str, file_name: str) -> None:
        self.redirect = self._load_redirect(dir_path, file_name)

    def __getitem__(self, key: str) -> Dict:
        return self._redirect(key)

    def _load_redirect(self, dir_path, file_name) -> Dict:
        redirect: Dict = {}
        try:
            with open(os.path.join(dir_path, file_name), encoding='utf-8') as redirect_file:
                for line in redirect_file.readlines():
                    line = line.split('\t->\t')
                    if len(line) == 2:
                        from_redirect = line[0]
                        to_redirect = line[1]
                        redirect[from_redirect] = to_redirect
        except Exception as e:
            print(e)
            return {}
        return redirect

    def _redirect(self, link: str) -> Dict:
        query_result: Dict = {}
        redirect_links: Set = set()

        while link in self.redirect:
            redirect_links.add(link)
            link = self.redirect[link]
        query_result["similar"] = redirect_links
        query_result["redirect"] = link

        return query_result


class TreeToGraph:
    """
    Query에 대해 파싱한 QueryTree에서 연결 가능한 노드들을 connected 시키는 클래스
    """
    def __init__(self, graph: Dict, query: str) -> None:
        self.graph: Dict = graph
        self.query = query
        self.query_tree: Dict = self._load_query()

    def _connect(self, node1: str, node2: str):
        """
        전체 그래프에 node1->node2가 연결되어 있다면, query에서 node1-> node2로 연결하는 함수
        :param node1: 문서1
        :param node2: 문서2
        :return:
        """
        if node1 in self.graph:
            if node2 in self.graph[node1]:
                if node1 not in self.query_tree:
                    self.query_tree[node1] = []
                self.query_tree[node1].append(node2)

    def tree_to_graph(self):
        query_keys: List = list(self.query_tree[self.query])
        for node1 in tqdm(query_keys):
            for node2 in query_keys:
                if node1 != node2:
                    self._connect(node1, node2)
        return self.query_tree

    def _load_query(self) -> Dict:
        with open(f'./data/result/{self.query}.pkl', 'rb') as pkl:
            query_tree = pickle.load(pkl)
        return query_tree

    def save_query_graph(self, visualize=False):
        with open(f'./data/result/{self.query}_graph.pkl', 'wb') as pkl:
            pickle.dump(self.query_tree, pkl)
        if visualize:
            self._visualize()

    def _visualize(self):
        visualize = json.dumps(self.query_tree, indent=4, ensure_ascii=False)
        print(visualize)
