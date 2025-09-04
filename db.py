from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv() # Loads all your environment variables into your program.

# Connect to Mongo Atlas Cluster
mongo_client = MongoClient(os.getenv("MONGO_URI")) # This is used secure our link / password

# Access database
event_manager_db = mongo_client["event_manager_db"]

# Pick a collection to operate on
events_collection = event_manager_db["events"]