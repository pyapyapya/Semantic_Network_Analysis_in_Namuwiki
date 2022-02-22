from typing import List, Dict, Set
import re
import sys
import os

from tqdm import tqdm


class PatternMatching:
    """
    정규식을 이용해 링크와 텍스트를 전처리 해주는 클래스
    """
    def __init__(self) -> None:
        self.url_pattern = re.compile('http[s]?://[\w./?=#&%]+')
        self.link_pattern = re.compile('\[\[[\w()/.:|\s]+\]\]')
        self.file_pattern = re.compile('[:]?파일:')

    def get_links(self, doc):
        """

        :param doc:
        :return:
        """
        links = {link[2:].split('|')[0].replace(']]', '') for link in self.link_pattern.findall(doc)}
        links = {link for link in links if not self.url_pattern.match(link)}
        links = {link for link in links if not self.file_pattern.match(link)}
        links = {link.strip().replace('분류:', '') for link in links}
        return links

    def get_hierarchy(self, doc):
        clean = lambda link: link.replace('[', '').replace(']', '')
        lines = doc.split('\n')
        parents = {clean(link) for line in lines for link in self.link_pattern.findall(line) if ' * 상위 문서 :' in line}
        children = {clean(link) for line in lines for link in self.link_pattern.findall(line) if ' * 하위 문서 :' in line}
        relateds = {clean(link) for line in lines for link in self.link_pattern.findall(line) if ' * 관련 문서 :' in line}
        category = {clean(link.replace('분류:', '')).strip() for line in lines for link in self.link_pattern.findall(line)
                    if '분류:' in line}
        return parents, children, relateds, category

    def get_text(self, doc):
        is_table = lambda line: '||' in line
        is_include = lambda line: '[include(' in line
        return [self.clean(line) for line in doc.split('\n') if (not is_include(line)) and (not is_table(line))]

    def clean(self, line):
        """
        위키 데이터 문법 전처리 중에 발생하는 예외 케이스들을 처리
        :param line: 한 document의 텍스트 한 라인
        :return:
        """
        line = line.replace("'''", "").replace('|', ' ').replace('[*', '').replace('[', '').replace(']', '').replace(
            '=', '').replace('\\', '').replace('-', '').replace('~', '').replace('(...)', '.')
        line = line.replace("\'", "'")
        for url in self.url_pattern.findall(line):
            line = line.replace(url, ' ')
        if line and (line[0] == '>' or line[0] == '*'):
            line = line[1:].strip()
        return line


class TransformData(PatternMatching):
    """
    전처리된 데이터를 이용하여 그래프, 텍스트 데이터로 변환하는 클래스
    """
    def __init__(self, namuwiki: List[Dict]) -> None:
        super().__init__()
        self.namuwiki: List[Dict] = namuwiki
        self.redirect: Dict = {}
        self.graph: Dict = {}

        self.n_docs = len(namuwiki)
        self.n_nodes = 0
        self.n_edges = 0
        self.node_degree: List[int] = []

    def to_graph(self) -> Dict:
        for i, entity in enumerate(tqdm(self.namuwiki)):
            title = entity.get('title', '')
            if not title: continue

            title_lower = title.lower()
            if '.jpg' in title_lower or '.gif' in title_lower or '.png' in title_lower:
                continue

            links: Set = self.get_links(entity.get('text', ''))
            if links:
                linked_entities: Set = self._get_linked_entities(title, links)
                self.graph[title] = linked_entities
                len_linked_entities: int = len(linked_entities)
                self.n_edges += len_linked_entities
                self.n_nodes += 1
                self.node_degree.append(len_linked_entities)
        sys.stdout.write(f'Total Docs: {self.n_docs}\n')
        sys.stdout.write(f'Total Nodes: {self.n_nodes}\n')
        sys.stdout.write(f'Total Edges: {self.n_edges}\n')

        sys.stdout.write('\nTo Graph Parsing done .. \n\n')

        return self.graph

    def to_text(self, directory, max_num_files=10000):
        """
        텍스트를 전처리하고, redirect문서와 index 문서를 생성하는 함수
        :param directory: directory path
        :param max_num_files: max_num_files 수 만큼 한 폴더에 각 문서의 txt 파일 생성
        :return:
        """
        n_saved = 0
        subdirectory = 0

        with open('%s/index.txt' % directory, 'w', encoding='utf-8') as fi:
            with open('%s/redirect.txt' % directory, 'w', encoding='utf-8') as fr:
                for i, entity in enumerate(tqdm(self.namuwiki)):
                    doc = entity.get('text', '')
                    text = ''.join(self.get_text(doc)).strip()
                    if not text:
                        continue

                    title = entity.get('title', '')

                    if text[:9] == '#redirect':
                        hyperlink = text[10:].strip()
                        fr.write('%s\t->\t%s\n' % (title, hyperlink))
                        self.redirect[title] = hyperlink
                        continue

                    with open('%s/%d/%d.txt' % (directory, subdirectory, n_saved), 'w', encoding='utf-8') as fo:
                        fo.write('%s\n' % text)

                    fi.write('%s\t%s\n' % (title, '%d/%d' % (subdirectory, n_saved)))

                    n_saved += 1
                    if n_saved % max_num_files == 0:
                        subdirectory += 1
                        if not os.path.exists('%s/%d/' % (directory, subdirectory)):
                            os.makedirs('%s/%d/' % (directory, subdirectory))

        sys.stdout.write('\nTo Text PreProcessing & Parsing done')

    def _redirect_link(self, link: str) -> Set:
        """
        redirect가 필요한 link 중 여러 번 redirect 해야 하는 경우 최종 link로 연결
        redirect link 자체도 충분한 의미를 가지고 있으므로 이를 return

        :return: str redirect_link
        """
        redirect_links: Set = set()
        while link in self.redirect:
            redirect_links.add(link)
            link = self.redirect[link]
        return redirect_links

    def _get_linked_entities(self, title: str, links: Set) -> Set:
        """
        document title에 속한 link에서 redirect link와 중복 제거한 link를 구한다.
        :param title: str 문서의 title
        :param links: List 문서에 걸려있는 links
        :return: Set redirect와 중복 제거한 links
        """
        linked_entities: Set = self.graph.get(title, set())
        for link in links:
            if link in self.redirect:
                redirect_link: Set = self._redirect_link(link)
                linked_entities.update(redirect_link)
            linked_entities.add(link)
        return linked_entities
