from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from pathlib import Path
from string import punctuation
from tqdm import tqdm
import re, math

BASE_DIR = Path(__file__).resolve().parent
IN_DIR = BASE_DIR / 'Clean'

stemmer = StemmerFactory().create_stemmer()
stopword = StopWordRemoverFactory().create_stop_word_remover()

tf, df, idf = {}, {}, {}

def get_text(tags, text):
    result = ''
    for tag in tags:
        try:
            result += re.search(f'<{tag}>(.*?)</{tag}>', text).group(1) + ' '
        except AttributeError:
            result += str(re.search(f'<{tag}>(.*?)</{tag}>', text)) + ' '
    return result

def index(hashs, terms):
    for word in terms:
        if word in hashs:
            hashs[word] += 1
        else:
            hashs[word] = 1    

print('Indexing ...')
for path in sorted(IN_DIR.glob('*/*.html')):
    with open(path.resolve(), 'r', encoding='utf-8') as file:
        df[path.name] = dict()

        content = get_text(['title', 'top', 'middle', 'bottom'], file.read())
        content = content.translate(str.maketrans('','', punctuation))
        content = stopword.remove(content)
        terms = stemmer.stem(content.lower()).split()

        index(df[path.name], terms)
        index(tf, terms)
print('Indexing done!\n')

print('Calculating idf for terms...')
for term, freq in tf.items():
    df_i = 0
    for doc, tf_doc in df.items():
        df_i += 1 if term in tf_doc else 0
    idf[term] = (1 + math.log2(len(df)/df_i)) if df_i != 0 else 1
print('Calculated!\n')

with open(BASE_DIR / 'words_score.txt', 'w', encoding='utf-8') as file:
    print('Writing words score to text file ...')
    for term, freq in tqdm(tf.items()):
        file.write(term + ' ::')
        for doc, tf_doc in df.items():
            tf_i = tf_doc[term] / sum(tf_doc.values()) if term in tf_doc else 0
            idf_i = idf[term]
            w = float(tf_i * idf_i)
            if w > 0:
                file.write(f' %s:%.3f' % (doc, w))
        file.write('\n')
    print('Done!')