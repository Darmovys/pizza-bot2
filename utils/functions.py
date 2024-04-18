import pymongo
from bson import ObjectId

import os

client = pymongo.MongoClient("Insert your MongoDB URL")
db = client.pizza_delivery

coll_pizzas = db.pizzas


def get_pizzas():
    arr = []
    for pizza in coll_pizzas.find():
        arr.append(pizza)
    return arr


def file_exists(filename):
    return os.path.isfile(os.path.join('./static/Img/', filename))


def insert_object(data):
    pizza = {
        "imageUrl": data["imageUrl"],
        "title": data["title"],
        "types": data["types"],
        "sizes": data["sizes"],
        "price": data["price"]
    }
    coll_pizzas.insert_one(pizza)


def update_pizza_title(data, message):
    coll_pizzas.update_one({"_id": ObjectId(data)}, {'$set': {"title": message}})


def update_pizza_types(data, message):
    coll_pizzas.update_one({"_id": ObjectId(data)}, {'$set': {"types": message}})


def insert_pizza_size(data, message):
    coll_pizzas.update_one({"_id": ObjectId(data)}, {'$push': {"sizes": {'$each': [message], "$sort": 1}}})


def delete_pizza_size(data, message):
    coll_pizzas.update_one({"_id": ObjectId(data)}, {'$pull': {"sizes": message}})


def update_pizza_size(data, index, message):
    coll_pizzas.update_one({"_id": ObjectId(data)}, {'$set': {"sizes.{index}".format(index=index): message}})
    coll_pizzas.update_one({"_id": ObjectId(data)}, {'$push': {"sizes": {'$each': [], "$sort": 1}}})


def update_pizza_price(data, message):
    coll_pizzas.update_one({"_id": ObjectId(data)}, {'$set': {"price": message}})


def update_pizza_photo(data, message):
    coll_pizzas.update_one({"_id": ObjectId(data)}, {'$set': {"imageUrl": message}})


def delete_pizza(data):
    coll_pizzas.delete_one({"_id": ObjectId(data)})
