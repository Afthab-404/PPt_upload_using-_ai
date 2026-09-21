from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017"

client = MongoClient(MONGO_URI)

db = client["ai_presentation_builder"]

presentations_collection = db["presentations"]