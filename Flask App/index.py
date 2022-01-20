from flask import Flask
from pymongo import MongoClient
import pymongo
app = Flask(__name__)

@app.route('/')
def index():
    client = MongoClient("mongodb://username:password@mongodb-service")
    db = client["milestone3"]
    col = db["data"]
    cursor = col.find()
    for text_fromDB in cursor:
        text = str(text_fromDB['name'].encode('utf-8'))
    print(text)
    return("<h1>"+text+" has reached Milestone 3 and is king of the mountain!</h1>")

if __name__ == "__main__":
    from waitress import serve
    app.run(host="0.0.0.0",debug=True)