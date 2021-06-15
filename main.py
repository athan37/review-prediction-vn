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

    def tokenize(self, text):
        #Assume that we are in the directory outside the tokenizer

        import os
        #Change dir and call the tokenizer
        current_dir = os.getcwd()
        path = os.path.join(current_dir, "XuLyNgonNguTuNhien")
        os.chdir(path)
        #1. Write the text as a text file
        with open("in_text.txt", "w", encoding="utf-8") as file:
            file.write(text)
        os.system("vnTokenizer.bat -i in_text.txt -o out_text.txt")
        #3. Get result and change back to current directory
        with open("out_text.txt", "r", encoding="utf-8") as file:
            new_text = file.read()

        os.chdir(current_dir)
        return new_text

    def predict(self, reviews, probability=True):
        if len(reviews) >= self.min_length:
            dict_   = {"-1": "negative", "1": "positive", "0": "neutral" }
            print("=========================Tokenizing=================================")
            reviews = self.tokenize(reviews)

            print("=========================Predicting=================================")
            [pred]   = self.predictor.predict_proba(self.preprocessor.transform([reviews]))
            import numpy as np
            max_idx  = np.argmax(pred)
            pred_label      = self.predictor.classes_[max_idx]
            pred_proba      = round(pred[max_idx] * 100, 1) #Convert to %
            if probability:
                return f"{dict_[str(pred_label)]} : {pred_proba}%"
            else:
                return f"{dict_[str(pred_label)]}"
        else:
            return "Text is too short"

# #Testing
# if __name__ == "__main__":
#     precitor = Predictor(min_length = 0)
#     text = """
#     App này quá tệ, tôi rất không hài lòng. Chậm quá mức
#     """
#     print(precitor.predict(text))