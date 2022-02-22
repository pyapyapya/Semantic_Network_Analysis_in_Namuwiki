from typing import List, Dict, Tuple
import pickle
import sys

import ijson

from transform import TransformData
from file_manager import FileManager


class ExtractWikiData:
    """
    namuwiki는 각 Document를 '나무위키 문법'을 포함하여 저장하고 있다.
    따라서 정제된 텍스트 데이터를 얻기 위해 데이터를 전처리를 하는 클래스이다.

    """
    def __init__(self,directory: str,  max_docs: int = 10000, debug=False):
        self.max_docs: int = max_docs
        self.debug = debug
        self.directory = directory

        self.documents: List[Dict] = self.parse_namuwiki_json()

    def parse_namuwiki_json(self) -> List[Dict]:
        """
        namuwiki DB dump한 json 파일을 파싱하는 과정. 메모리가 부족하여 ijson을 통해 generator (line-by-line)으로 읽는 함수.
        json 문서 구조는 List[Dict] 형식으로 구성됨.
        prefix: 해당 문서가 어떤 내용을 포함하고 있는지. ex) title, contributor, text..
        event:
        value: prefix가 포함하고 있는 내용
        :param: max_docs: int debug=True 일 경우 max_docs 만큼 진행
        :param: debug: Bool debug 여부
        :return: List[Dict]
        """
        json_path: str = './data/namuwiki_20210301.json'
        namuwiki: List = []
        with open(json_path, 'rb') as json_file:
            doc: Dict = {}
            doc_idx = 1
            for prefix, event, value in ijson.parse(json_file):
                """
                    TODO: 분류, 목차에 해당하는 Data Category를  진행해야 함.
                """
                if prefix == 'item.title':
                    doc["title"] = value
                if prefix == 'item.text':
                    doc["text"] = value
                    doc_idx += 1
                    namuwiki.append(doc)
                    doc: Dict = {}
                    if doc_idx % self.max_docs == 0:
                        if self.debug:
                            break
                        sys.stdout.write(f'Reading Json: {doc_idx}\n')
        return namuwiki


def main():
    max_docs = 10000
    directory_path = './data/result'
    extract_wikidata = ExtractWikiData(max_docs=max_docs, directory=directory_path, debug=False)
    documents: List[dict] = extract_wikidata.parse_namuwiki_json()
    transform_data = TransformData(documents)
    transform_data.to_text(directory=directory_path)
    graph: Dict = transform_data.to_graph()
    file_manager = FileManager()
    file_manager.save_graph(graph)


main()
