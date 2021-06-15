from flask import Flask
from flask_restful import Resource, Api, reqparse, abort, marshal, fields

from main import Predictor

app = Flask(__name__)
api = Api(app)

reviews = [
    {
    "summary" : "Good",
    "content" : "Very good",
    "percentage": True
    },
    {
    "summary" : "Not Bad",
    "content" : "Sure good good",
    "percentage": False
    },
    {
    "summary" : "Hei, that's greate",
    "content" : "I rove it",
    "percentage": False
    },
]

reviewFields = {
    "summary": fields.String,
    "content": fields.String,
    "percentage": fields.Boolean,
}

class Prediction(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("summary", type=str, required=False,
            location="json", help="The content must be provided to predict the review")
        self.reqparse.add_argument("content", type=str, required=True,
            location="json", help="The content must be provided to predict the review")
        self.reqparse.add_argument("percentage", type=str, required=False,
            location="json", help="Can be optional for the percentage")

        super(Prediction, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()

        predictor = Predictor(min_length = 0)

        text = args["content"]
        if "summary" in args:
            text = args["summary"] + text

        if "percentage" in args:
            result   = predictor.predict(text, probability=args["percentage"])
        else:
            result   = predictor.predict(text)

        return result

    def get(self):
        return "Post a review in this link to get prediction"

api.add_resource(Prediction, "/prediction")
