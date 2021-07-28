from flask import Flask, redirect, url_for, render_template
from flask_restful import Resource, Api, reqparse, request, inputs
import dateutil.parser as parser
import datetime
import pymongo
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

class Buzzs(Resource):
    def __init__(self):
        from pymongo import MongoClient
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("appId",     type=str, required=True,  location="json", help="The appstore id of the app that you want to fetch reviews from")
        self.reqparse.add_argument("page",      type=int, required=False, location="json", help="The page that contain the data. Default is 1")
        self.reqparse.add_argument("perPage",   type=int, required=False, location="json", help="The page that contain the data. Default is 24")
        self.reqparse.add_argument("fromDate",  type=str, required=False, location="json", help="The begin date as a string with format YYYY-mm-dd (Ex: '2021-07-28'), the default is all days from the past")
        self.reqparse.add_argument("toDate",    type=str, required=False, location="json", help="The end date, YYYY-mm-dd (Ex: 2021-07-28) the default is today")
        self.reqparse.add_argument("query",     type=inputs.regex('^.+:.+$'), required=False, location="json", help="Query separated by a colon (:), only applicable to text field [appName, sentiment]: example: 'sentiment: negative' ")
        #Connect with mongo
        self.client     = MongoClient("mongodb+srv://user1234:user1234@cluster0.zmdnb.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
        self.db         = self.client["main"]
        self.collection = self.db.reviews

    def post(self):
        args = self.reqparse.parse_args()
        appId    = args["appId"]
        page     = args["page"]
        perPage  = args["perPage"]
        fromDate = args["fromDate"]
        toDate   = args["toDate"]
        addQuery = args["query"]

        data = {
            "total"  : 0,
            "results": []
        }

        query      = {}
        queryDate  = {}
        page    = page if page else 1
        perPage = perPage if perPage else 24
        toDate  = toDate  if toDate else datetime.datetime.now().isoformat() #default is today

        query["appId"] = appId


        if fromDate:
            queryDate  = {
                '$gte': parser.parse(fromDate).isoformat()
            }

        queryDate = {
            **queryDate,
            '$lt': parser.parse(toDate).isoformat()
        }


        query["publishDate"] = queryDate

        if addQuery:
            [key, val] = addQuery.split(":")
            query = {
                **query,
                f"{key.strip()}" : val.strip()
            }

        cursor = self.collection.find(query)

        cursor.sort("publishDate", pymongo.DESCENDING)

        cursor = cursor.skip((page - 1) * perPage  if page > 0 else 0);

        cursor.limit(perPage)

        data["total"]   = cursor.count()
        data["results"] = list(cursor)

        return data, 200


class Apps(Resource):
    def __init__(self):
        from pymongo import MongoClient
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("keyword", type=str, required=True,  location="json", help="The keyword that you remember from the app: Ex: BIDV")
        #Connect with mongo
        self.client     = MongoClient("mongodb+srv://user1234:user1234@cluster0.zmdnb.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
        self.db         = self.client["main"]
        self.collection = self.db.reviews

    def post(self):
        args    = self.reqparse.parse_args()
        keyword = args["keyword"]
        try:
            res = self.collection.aggregate([{
                '$search': {
                  'index': 'text',
                  'text': {
                    'query': keyword,
                    'path': {
                      'wildcard': '*'
                    }
                  }
                }
              },
            ]).next()
            return f'App name: {res["appName"]} - appId: {res["appId"]}'
        except Exception as e:
            return "There is no match for this search"

    def get(self):
        cursor = self.collection.aggregate([
            {
                '$project': {
                    'appName': 1,
                    'appId': 1
                }
            }, {
                '$group': {
                    '_id': {
                        'appId': '$appId',
                        'appName': '$appName'
                    }
                }
            }
        ])

        unwind = lambda doc : doc["_id"]

        res = [unwind(doc) for doc in cursor]

        return res, 200


api.add_resource(Prediction, "/prediction", endpoint="prediction")
api.add_resource(Buzzs, "/buzzs", endpoint="buzzs")
api.add_resource(Apps, "/search", endpoint="search")


@app.route('/')
def index():
    return redirect(url_for("prediction"))

if __name__ == "__main__":
  app.run()
