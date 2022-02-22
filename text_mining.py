"""
1. Query Graph를 load하고, TF-IDF 행렬을 만듬
2. CSR_Matrix 를 save & load
3. 문서 간Cosine Similarity 구하기
4. Query Graph에 적용
5. Network Analysis 적용
6. 시각화
"""
import itertools
from typing import Dict, List

from scipy.sparse.csr import csr_matrix
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from file_manager import FileManager


class TextMining:
    """
    Dict 형태의 Graph를 TF-IDF 행렬로 변환후, CSR_Matrix 추출.
    Cosine Similarity 기반으로 문서간 유사도 구하는 클래스
    """
    def __init__(self, query: str = '') -> None:
        self.query = query
        self.query_graph: Dict = self.load_graph(self.query)
        self._get_cosine_similarity()

    def _to_tf_idf(self) -> csr_matrix:
        """
        graph를 TF-IDF Matrix로 변환
        :return: csr_matrix
        """
        # corpus = self.dict_to_array()
        # print(corpus)
        # vectorizer = CountVectorizer(lowercase=False,
        #                              tokenizer=lambda x: x.split('\t'))
        tfidf = TfidfVectorizer(min_df=0, max_df=1)
        tfidf_vector: csr_matrix = tfidf.fit_transform(self.query_graph)
        # tfidf_vector = tfidf_vector.toarray()
        print(tfidf_vector)
        print()
        # print(tfidf.get_feature_names())
        # print(type(tfidf_vector))

        self.save_tfidf(self.query, tfidf_vector)
        return tfidf_vector

    def _to_csr_matrix(self):
        """
        COO Matrix를 CSR Matrix로 변환
        TOIDF Matrix load시 coo Matrix
        :return:
        """
        pass

    def _get_cosine_similarity(self):
        """
        cosine similarity를 이용해각 문서의 유사도를 측정
        :return:
        """
        tfidf_vector: csr_matrix = self._to_tf_idf()
        # tfidf_dense_vector = tfidf_vector.todense()
        cosine_similarity_matrix = cosine_similarity(tfidf_vector, tfidf_vector, dense_output=False)
        print(cosine_similarity_matrix)
        return cosine_similarity_matrix

    def dict_to_array(self) -> List[List[str]]:
        corpus: List = []
        for key in self.query_graph.keys():
            corpus.append('\t'.join(self.query_graph[key]).split('\t'))
        return corpus

    @staticmethod
    def load_graph(query: str) -> Dict:
        file_manager: FileManager = FileManager()
        query_graph: Dict = file_manager.load_graph(query=query)
        return query_graph

    @staticmethod
    def save_tfidf(query: str, tfidf_vector: csr_matrix):
        file_manager: FileManager = FileManager()
        file_manager.save_tfidf(query, tfidf_vector)


def main():
    query = 'I.O.I'
    text_mining = TextMining(query=query)


main()
