from sklearn.base import BaseEstimator, TransformerMixin
import re
from collections import Counter
import nltk
import urlextract
import numpy as np
#Define some helper class instances
url_extractor = urlextract.URLExtract()
stemmer = nltk.PorterStemmer()
from html import unescape

def html_to_plain_text(html):
    text = re.sub('<head.*?>.*?</head>', '', html, flags=re.M | re.S | re.I)
    text = re.sub('<a\s.*?>', ' HYPERLINK ', text, flags=re.M | re.S | re.I)
    text = re.sub('<.*?>', '', text, flags=re.M | re.S)
    text = re.sub(r'(\s*\n)+', '\n', text, flags=re.M | re.S)
    return unescape(text)

class ReviewToWordCounterTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, lower_case=True, replace_num=True,
                 punctuation=False, remove_url=True, stemming=True, remove_tag=True):
        self.lower_case  = lower_case
        self.replace_num = replace_num
        self.punctuation = punctuation
        self.remove_url  = remove_url
        self.stemming    = stemming
        self.remove_tag  = remove_tag
    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X_transformed = []
        for text in X:
            if self.remove_tag:
                text = html_to_plain_text(text)
            if self.lower_case:
                text = text.lower()
            if self.replace_num:
                text = re.sub(r'\d+(?:\.\d*(?:[eE]\d+))?', 'NUMBER', text)
            if not self.punctuation:
                text = re.sub(r'\W+', ' ', text, flags=re.M)
            if self.remove_url and url_extractor is not None:
                urls = list(set(url_extractor.find_urls(text)))
                urls.sort(key=lambda url: len(url), reverse=True)
                for url in urls:
                    text = text.replace(url, " URL ")


            #After removing the tag, have to delete all the new line and \r
            text = re.sub('\r?\n', ' ', text)
            #Count word by splitting them
            word_counts = Counter(text.split()) #Assume that the dataset has been tokenized with noun1_noun2

            if self.stemming and stemmer is not None:
                stemmed_word_counts = Counter()
                for word, count in word_counts.items():
                    stemmed_word = stemmer.stem(word)
                    stemmed_word_counts[stemmed_word] += count
                word_counts = stemmed_word_counts

            X_transformed.append(word_counts)
        return np.array(X_transformed)
