from flask import Flask
from flask_restful import Resource, Api, reqparse, abort, marshal, fields

from main import Predictor

app = Flask(__name__)
api = Api(app)

# reviews = [
#     {
#     "summary" : "Good",
#     "content" : "Very good",
#     "percentage": True
#     },
#     {
#     "summary" : "Not Bad",
#     "content" : "Sure good good",
#     "percentage": False
#     },
#     {
#     "summary" : "Hei, that's greate",
#     "content" : "I rove it",
#     "percentage": False
#     },
# ]
#
# reviewFields = {
#     "summary": fields.String,
#     "content": fields.String,
#     "percentage": fields.Boolean,
# }

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
                    print("Make sure the length of summaries and contents are equal")
                    return 400 #Bad request

                reviews = [f"{summaries[i]} {contents[i]}" for i in range(len(contents))]

                results = self.predictor.predictAll(reviews, probability=args["percentage"])

                return {"results" : results}, 201
        else:
            if args["content"] is None:
                return 400
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
        return 400

    def get(self):
        return "Post a review in this link to get prediction"

api.add_resource(Prediction, "/prediction")

if __name__ == "__main__":
  app.run()
