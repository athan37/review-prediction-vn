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
        return render_template("prediction/index.html")

api.add_resource(Prediction, "/prediction", endpoint="prediction")


@app.route('/')
def index():
    return redirect(url_for("prediction"))

if __name__ == "__main__":
  app.run()
