from flask import Flask 
import certifi
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["SECRET_KEY"] = "f2f85cba3cda3f825e152cda1634cf05d3886b2c"
app.config["MONGO_URI"] = "mongodb+srv://Titania:Mahadev@cluster0.zq3w2cn.mongodb.net/titania_trading"

# setup mongo_db
# mongodb_client = PyMongo(app)
mongodb_client = PyMongo(app,tlsCAFile=certifi.where())
db = mongodb_client.db

from application import routes