from sklearn.base import BaseEstimator, TransformerMixin
import re
from collections import Counter
import numpy as np

class ReviewToWordCounterTransformer(BaseEstimator, TransformerMixin):
    '''
        This class will transform the training reviews to counter object and
        return the transformed data in a nunpy array.

        Attributes:
        ----------
        lower_case : bool
            Set to true if wanting all text to be lower
        punctuation: bool
            Set to false to delete all punctuation
    '''

    def __init__(self, lower_case=True, punctuation=False):
        """
            Init the tranformer

        Params:
        -------
                lower_case : bool
                    Set to true if wanting all text to be lower
                punctuation: bool
                    Set to false to delete all punctuation
        """
        self.lower_case  = lower_case
        self.punctuation = punctuation

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        """
            Processing text, spliting them and turn each review into counter
            objects

        Params:
        -------
                X : np array
                    Array containing reviews
                y : None
                    Not important param
        Returns:
        --------
            np array:
                Transformed review data in a nunpy array.
        """
        X_transformed = []
        for text in X:
            if self.lower_case:
                text = text.lower()
            if not self.punctuation: #W+ means remove all non word chars
                text = re.sub(r'\W+', ' ', text, flags=re.M)

            #Count word by splitting them
            word_counts = Counter(text.split()) #Assume that the dataset has been tokenized with noun1_noun2
            X_transformed.append(word_counts)

        return np.array(X_transformed)
