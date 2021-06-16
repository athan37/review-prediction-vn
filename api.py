from flask import Flask, redirect, url_for, render_template
from flask_restful import Resource, Api, reqparse

from main import Predictor

app = Flask(__name__)
api = Api(app)

class Prediction(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("summary", type=str, required=False,
            location="json", help="The content must be provided to predict the review")
        self.reqparse.add_argument("content", type=str, required=False,
            location="json", help="The content must be provided to predict the review")
        self.reqparse.add_argument("summaries", type=list, required=False,
        ############################# Multiple reviews =========================
            location="json", help="Mutiple contents must be paired with mutiple summaries")
        self.reqparse.add_argument("contents", type=list, required=False,
            location="json", help="Mutiple contents must be paired with mutiple summaries")
        self.reqparse.add_argument("percentage", type=str, required=False,
            location="json", help="Can be optional for the percentage")

        self.predictor = Predictor(min_length = 0)
        super(Prediction, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        if "contents" in args and args["contents"] is not None:
            contents = args["contents"]
            if "summaries" in args and args["contents"] is not None:
                summaries = args["summaries"]
                if len(contents) != len(summaries):
                    return f"Make sure the length {len(summaries)} of summaries and length {len(contents)} of contents are equal", 400 #Bad request

                reviews = [f"{summaries[i]} {contents[i]}" for i in range(len(contents))]

                results = self.predictor.predictAll(reviews, probability=args["percentage"])

                return {"results" : results}, 201
        else:
            if args["content"] is None:
                return "Please input content", 400
            text = args["content"]
            if "summary" in args and args["summary"] is not None:
                text = f'{args["summary"]} {text}'

            result = ""
            if "percentage" in args and args["percentage"]:
                pred_label, pred_proba = self.predictor.predict(text, probability=True)
                return {"result" : pred_label, "probability" : pred_proba}, 201
            else:
                result   = self.predictor.predict(text)
                return {"result" : result}, 201
        #Definitely bad request
        return "Something wrong", 400

    def get(self):
        return {"Instruction" : "Send POST request to this to get result. If predicting multiple comments, pass in summaries and contents. Destination of data is json",
                "Params" : {
                    "summary" : "String: The summary of the review if extists",
                    "content" : "String: The content of the review",
                    "percentage" : "Boolean: Percentage of the prediction",
                    "summaries" : "List(String): The list of summaries of the review if extists",
                    "contents" : "List(String): The list of contents of the review",
                },
                "Returns" : {
                    "If params has summary and content" : {
                        "If percentage is not provided" : "The prediction, either positive, neutral, or negative",
                        "If percentage is provided" : "The prediction with the percentage"
                    },
                    "If params has summaries and contents" : {
                        "If percentage is not provided" : "The predictions, either positive, neutral, or negative",
                        "If percentage is provided" : "The predictions with the percentage"
                    }
                },
                "Examples in python" : [
                    {
                        "Request" :
                        {
                            "1. Import requests library" : "import requests",
                            "2. Define the url" : "https://review-prediction-vn.herokuapp.com/prediction",
                            "3. Define the data" : {"data" : {"summary" : "hey", "content": "that\'s great", "percentage": True}},
                            "4. Post the data to json destination" : 'response = requests.post(url=url, json=data)',
                            "5. Get the result" : 'response.text'
                        },
                        "Response" : {
                            "result"     : 'positive',
                            'probability': 94.5
                            }
                    },
                    {
                        "Request" :
                        {
                            "1. Import requests library" : "import requests",
                            "2. Define the url" : "https://review-prediction-vn.herokuapp.com/prediction",
                            "3. Define a list of summaries and assign it to the variable summaries" : {
                                    "summaries" : ["Hay", "Tốt"]
                                },
                            "4. Define a list of contents and assign it to the variable contents" : {
                                    "contents" : ["Tốt thật đấy", "Ổn app"]
                                },
                            "5. Define the data" : {"data" : {"summaries" : "summaries", "contents": "contents"}},
                            "6. Post the data to json destination" : 'response = requests.post(url=url, json=data)',
                            "7. Get the result" : 'response.text'
                        },
                        "Response" : [[0, "positive"], [1, "positive"]]
                    }
                ]
            }

api.add_resource(Prediction, "/prediction", endpoint="prediction")


@app.route('/')
def index():
    return redirect(url_for("prediction"))

if __name__ == "__main__":
  app.run()
