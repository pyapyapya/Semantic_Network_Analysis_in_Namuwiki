from typing import Dict
import os
import pickle
import json

from scipy.sparse.csr import csr_matrix
from scipy.sparse.coo import coo_matrix
from scipy.io import mmwrite, mmread


class FileManager:
    """
    각 클래스에서 나오는 데이터들의 load, save를 관리하는 클래스
    """
    def __init__(self, dir_path=None) -> None:
        if dir_path is None:
            dir_path = './data/result'
        self.dir_path = dir_path
        self.graph_file_name = 'graph.pkl'

        self.__init()

    def load_graph(self, query=''):
        if query == '':
            with open(os.path.join(self.dir_path, self.graph_file_name), 'rb') as pkl:
                wiki_graph: Dict = pickle.load(pkl)
        else:
            wiki_graph: Dict = self.load_query_graph(query=query)
        return wiki_graph

    def save_graph(self, wiki_graph: Dict):
        with open(os.path.join(self.dir_path, self.graph_file_name), 'wb') as f:
            pickle.dump({word: list(links) for word, links in wiki_graph.items()}, f)

    def load_query(self, query:str) -> Dict:
        with open(os.path.join(self.dir_path, query+'.pkl'), 'rb') as pkl:
            query_tree = pickle.load(pkl)
        return query_tree

    def save_query(self, query: str, query_tree: Dict, visualize=False):
        with open(os.path.join(self.dir_path, query+'.json'), 'w', encoding='utf-8') as json_file:
            json.dump(query_tree, json_file, ensure_ascii=False)
        with open(os.path.join(self.dir_path, query+'.pkl'), 'wb') as pkl:
            pickle.dump(query_tree, pkl)

        if visualize:
            self._visualize(query_tree)

    def load_query_graph(self, query: str) -> Dict:
        with open(os.path.join(self.dir_path, query+'_graph.pkl'), 'rb') as pkl:
            query_graph: Dict = pickle.load(pkl)
        return query_graph

    def save_query_graph(self, query: str, query_graph: Dict, visualize=False):
        with open(os.path.join(self.dir_path, query+'.json'), 'wt', encoding='UTF-8') as json_file:
            json.dump(query_graph, json_file, indent=4,  ensure_ascii=False)
        with open(os.path.join(self.dir_path, query+'_graph.pkl'), 'wb') as pkl:
            pickle.dump(query_graph, pkl)
        if visualize:
            self._visualize(query_graph)

    def load_tfidf(self, query: str) -> csr_matrix:
        mtx_path = os.path.join(self.dir_path, query+'.mtx')
        wiki_tdm: coo_matrix = mmread(mtx_path)
        wiki_tdm: csr_matrix = wiki_tdm.tocsr()
        return wiki_tdm

    def save_tfidf(self, query: str, tfidf_vector: csr_matrix):
        mtx_path = os.path.join(self.dir_path, query+'.mtx')
        mmwrite(mtx_path, tfidf_vector)

    @staticmethod
    def __init():
        if not os.path.exists('./data'):
            os.mkdir('./data')
        if not os.path.exists('./result'):
            os.mkdir('./result')

    @staticmethod
    def _visualize(data):
        visualize = json.dumps(data, indent=4, ensure_ascii=False)
        print(visualize)
