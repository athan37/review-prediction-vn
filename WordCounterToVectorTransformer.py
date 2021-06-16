from sklearn.base import BaseEstimator, TransformerMixin
from scipy.sparse import csr_matrix
from collections import Counter

class WordCounterToVectorTransformer(BaseEstimator, TransformerMixin):
    """
        Transform counters array to vector

        Attributes:
        ----------
        vocabulary_size : int
            the number of the most common words
        most_common_ : list
            The list of most common words and their counts
        vocabulary_ : dict_
            The word and index for each word in most common words. This is for
            indexing common words purpose

    """
    def __init__(self, vocabulary_size=1000):
        """
            Define size of the vocab here
        """
        self.vocabulary_size = vocabulary_size

    def fit(self, X, y=None):
        """
            Generate and indexing the vocabulary_
        """
        #Get common words of this training set, else, ignore the less common words
        total_count = Counter()
        for word_count in X:
            for word, count in word_count.items():
                total_count[word] += min(count, 10) #Avoid adding too much word, such as yeah *1000 for a spamming message
        most_common = total_count.most_common()[:self.vocabulary_size]
        self.most_common_ = most_common
        self.vocabulary_ = {word: index + 1 for index, (word, count) in enumerate(most_common)}
        return self

    def transform(self, X, y=None):
        """
            Make a sparse matrix for each comment. If the words doesn't exist
            in most common word, replace the data with 0

            Params:
            -------
                X: np array
                    Array contains each review as a counter object
        """
        rows = []
        cols = []
        data = []
        #Loop through each reviews
        for row, word_count in enumerate(X):
            #Analyze each review with the total vocab of this dataset
            for word, count in word_count.items():
                rows.append(row)
                cols.append(self.vocabulary_.get(word, 0)) #If non, replace it with 0
                data.append(count)
                
        return csr_matrix((data, (rows, cols)), shape=(len(X), self.vocabulary_size + 1))
