# http://localhost:8000 This link is what any frontend that want to engage your backend would have access to.
# http://localhost:8000/docs

# status_code=204, response_description="No content" >> This is how to add status codes and descriptions to the app.get().. you put it inside the function.

from fastapi import FastAPI
from db import events_collection
from pydantic import BaseModel
from bson.objectid import ObjectId
from utils import replace_mongo_id


class EventModel(BaseModel):
    title: str
    description: str


app = FastAPI()  # These two lines of code creates a server for you.


@app.get("/")
def get_home():
    return {"message": "You are on the homepage"}


# Events endpoints
@app.get("/events")
def get_events(title="", description="", limit=10, skip=0):
    """Gets all events from database"""
    events = events_collection.find(
        filter={
            "$or": [
                {"title": {"$regex": title, "$options": "i"}},
                {"description": {"$regex": description, "$options": "i"}},
            ]
        },
        limit = int(limit),
        skip = int(skip)
    ).to_list()
    # Return Response
    return {"data": list(map(replace_mongo_id, events))}


@app.post("/events")
def post_event(event: EventModel):
    """Insert event into database"""
    events_collection.insert_one(event.model_dump())
    # Return response
    return {"message": "Event added succesfully"}


@app.get("/events/{event_id}")
def get_event_by_id(event_id):
    """Get event from database by id"""
    event = events_collection.find_one({"_id": ObjectId(event_id)})
    # Return response
    return {"data": replace_mongo_id(event)}
