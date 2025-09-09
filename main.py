# http://localhost:8000 This link is what any frontend that want to engage your backend would have access to.
# http://localhost:8000/docs

# status_code=204, response_description="No content" >> This is how to add status codes and descriptions to the app.get().. you put it inside the function.

from fastapi import FastAPI, Form, File, UploadFile, HTTPException, status
from db import events_collection
from pydantic import BaseModel
from bson.objectid import ObjectId
from utils import replace_mongo_id
from typing import Annotated
import cloudinary
import cloudinary.uploader

# import cloudinary.api

# Configure Cloudinary

cloudinary.config(
    cloud_name="dx5tbpgob",
    api_key="257948316413835",
    api_secret="_U8C_w49y7IpJY4v0dpp9Uhbq0k",
)


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
        limit=int(limit),
        skip=int(skip),
    ).to_list()
    # Return Response
    return {"data": list(map(replace_mongo_id, events))}


@app.post("/events")
def post_event(
    title: Annotated[str, Form()],
    description: Annotated[str, Form()],
    flyer: Annotated[UploadFile, File()],
):
    # Upload flyer to cloudinary to get a url.
    upload_result = cloudinary.uploader.upload(flyer.file)
    """Insert event into database"""
    events_collection.insert_one(
        {
            "title": title,
            "description": description,
            "flyer": upload_result["secure_url"],
        }
    )
    # Return response
    return {"message": "Event added succesfully"}


@app.get("/events/{event_id}")
def get_event_by_id(event_id):
    # Check if event_id is valid
    if not ObjectId.is_valid(event_id):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid mongo id received!"
        )
    """Get event from database by id"""
    event = events_collection.find_one({"_id": ObjectId(event_id)})
    # Return response
    return {"data": replace_mongo_id(event)}


@app.put("/events/{event_id}")
def replace_event(
    event_id,
    title: Annotated[str, Form()],
    description: Annotated[str, Form()],
    flyer: Annotated[UploadFile, File()],
):
    # Check if event_id is a valid mongo id
    if not ObjectId.is_valid(event_id):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid mongo received"
        )
    # Upload flyer to cloudinary to get a url.
    upload_result = cloudinary.uploader.upload(flyer.file)
    events_collection.replace_one(
        filter={"_id": ObjectId(event_id)},
        replacement={
            "title": title,
            "description": description,
            "flyer": upload_result["secure_url"],
        },
    )
    return {"message": "Event replaced succesffully"}


@app.delete("/events/{events_id}")
def delete_event(event_id):
    if not ObjectId.is_valid(event_id):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid Mongo Received!"
        )
    delete_result = events_collection.delete_one(filter={"_id": ObjectId(event_id)})
    if not delete_result.deleted_count:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No event found to delete")
    return {"message": "Event deleted succesfully"}