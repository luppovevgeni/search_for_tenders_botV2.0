import pymongo
from os import environ

client = pymongo.MongoClient(f"mongodb://{environ['HOST']}", int(environ["PORT"]))

#client = pymongo.MongoClient("localhost", 27017)

db = client["search_for_tenders"]

users = db["users"]

#users.update_many({}, {"$set": {"premium": True}})
