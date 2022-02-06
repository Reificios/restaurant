from xml.dom.minidom import Element
from fastapi import FastAPI, Query, HTTPException
from typing import Optional
from pydantic import BaseModel
from pymongo import MongoClient
from fastapi.encoders import jsonable_encoder

class Reservation(BaseModel):
    name : str
    time: int
    table_number: int

class ChangeReservation(BaseModel):
    name : str
    time: int
    table_number: int
    new_time: int
    new_table_number: int
    
client = MongoClient("mongodb://localhost:27017/")

# TODO fill in database name
db = client["restaurant"]

# TODO fill in collection name
collection = db["reservation"]

app = FastAPI()


# TODO complete all endpoint.
@app.get("/reservation/by-name/{name}")
def get_reservation_by_name(name: str):
    result = collection.find({"name":name},{"_id":0})
    my_res = []
    for r in result:
        my_res.append(r)
    print(my_res)
    return{
        "result": my_res
    }

@app.get("/reservation/by-table/{table}")
def get_reservation_by_table(table: int):
    result = collection.find({"table_number":table},{"_id":0}).sort("time")
    my_res = []
    for r in result:
        my_res.append(r)
    print(my_res)
    return{
        "result": my_res
    }
@app.post("/reservation")
def reserve(reservation : Reservation):
    r = jsonable_encoder(reservation)
    table = r["table_number"]
    time = r["time"]
    query = {"table_number":table,"time": time}
    result = collection.find_one(query,{"_id":0})
    if (table > 12) or (time > 24):
        raise HTTPException(404, f"Not valid input")
    elif result == None:
        x = collection.insert_one(r)
        return {
            "result" : "success"
        }
    else:
        raise HTTPException(404, f"Table is already reserved")

@app.delete("/reservation/delete/{name}/{table_number}")
def cancel_reservation(name: str, table_number : int):
    query = {"name" : name, "table_number" : table_number}
    collection.delete_many(query)
    return{
        "result" : "success"
    }

@app.put("/reservation/update/")
def update_reservation(reservation: ChangeReservation):
    r = jsonable_encoder(reservation)
    table = r["table_number"]
    time = r["time"]
    new_table = r["new_table_number"]
    new_time = r["new_time"]
    query = {"table_number":new_table,"time": new_time}
    result = collection.find_one(query,{"_id":0})
    if (new_table > 12) or (new_time > 24):
        raise HTTPException(404, f"Not valid input")
    elif result == None:
        x = collection.update_one({"table_number":table, "time": time},{"$set":{"table_number":new_table, "time": new_time}})
        return {
            "result" : "success"
        }
    else:
        raise HTTPException(404, f"Table is already reserved")