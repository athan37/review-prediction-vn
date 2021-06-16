 # -*- coding: utf-8 -*-
class Predictor:
    def __init__(self, min_length=50):
        #Import here as it doesn't need these outside this class
        import joblib
        from sklearn.linear_model import LogisticRegression
        #Import local file
        from WordCounterToVectorTransformer import WordCounterToVectorTransformer
        from ReviewToWordCounterTransformer import ReviewToWordCounterTransformer
        self.predictor    = joblib.load("model.pkl")
        self.preprocessor = joblib.load("preprocess.pkl")
        self.min_length   = min_length

    def predict(self, review, probability=False):
        if len(review) >= self.min_length:
            dict_   = {"-1": "negative", "1": "positive", "0": "neutral" }
            [pred]   = self.predictor.predict_proba(self.preprocessor.transform([review]))
            import numpy as np
            max_idx  = np.argmax(pred)
            pred_label      = self.predictor.classes_[max_idx]
            pred_proba      = round(pred[max_idx] * 100, 1) #Convert to %
            if probability:
                return dict_[str(pred_label)], pred_proba
            else:
                return dict_[str(pred_label)]
        else:
            return "Text is too short"

    def predictAll(self, reviews = [], probability=False):
        results = [(index, *self.predict(review, probability))
        if probability else (index, self.predict(review))
        for index, review in enumerate(reviews)]
        return results
