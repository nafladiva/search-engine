from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from string import punctuation
import sys, re, time

class Search:
    stemmer = StemmerFactory().create_stemmer()
    stopword = StopWordRemoverFactory().create_stop_word_remover()

    dictionary = {}

    def __init__(self):
        filescore = open('words_score.txt', 'r')
        lines = filescore.readlines()

        for line in lines:
            part = line.split(' :: ')
            term = part[0]
            self.dictionary[term] = {}
            weight_terms = part[1].split()
            for weight in weight_terms:
                doc, w = weight.split(':')
                self.dictionary[term][doc] = float(w)

    def get_title(self, text):
        return re.search('<title>(.*?)</title>', text).group(1)

    def get_url(self, text):
        return re.search('<url>(.*?)</url>', text).group(1)

    def get_content(self, tags, text):
        result = ''
        for tag in tags:
            try:
                result += re.search(f'<{tag}>(.*?)</{tag}>', text).group(1) + ' '
            except AttributeError:
                result += str(re.search(f'<{tag}>(.*?)</{tag}>', text)) + ' '
        return result

    def search(self, query, total):
        result = {}
        article = []
        article_with_seconds = {}

        query = query.translate(str.maketrans('','', punctuation))
        query = self.stopword.remove(query)
        query_terms = self.stemmer.stem(query.lower()).split()
        
        start = time.time()

        for term in query_terms:
            if term in self.dictionary.keys():
                for doc in self.dictionary[term].keys():
                    if doc not in result.keys():
                        result[doc] = float(self.dictionary[term][doc])
                    else:
                        result[doc] +=  float(self.dictionary[term][doc])

        sorted_result = sorted(result.items(), key=lambda x:x[1], reverse=True)

        for doc, w in sorted_result[:total]:
            if doc.startswith('detik'):
                dir_path = 'Clean/Scrap detik/'+doc
            elif doc.startswith('kompas'):
                dir_path = 'Clean/Scrap kompas/'+doc
            else:
                dir_path = 'Clean/Scrap liputan6/'+doc

            document = open(dir_path, 'r', encoding='utf-8').read()

            article.append({
                'title': self.get_title(document),
                'url': self.get_url(document),
                'content': self.get_content(['top', 'middle', 'bottom'], document)[:200].lstrip() + '...'
            })
            
        finish = time.time()
        proccess_time = round((finish - start), 5)
        article_with_seconds[proccess_time] = {}
        article_with_seconds[proccess_time] = article

        return article_with_seconds
