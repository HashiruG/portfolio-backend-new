from fastapi import FastAPI
from db import getDatabase
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import os

load_dotenv()

database = getDatabase()

#define collections
project_collection = database["projects"]
programming_skills_collection = database["programming_skills"]
web_skills_collection = database["web_skills"]
machine_learning_skills_collection = database["machine_learning_skills"]

#blob storage setup
azure_connection_string = os.getenv("AZURE_CONNECTION_STRING")
blob_service_client = BlobServiceClient.from_connection_string(azure_connection_string)
container_name = "images"
container_client = blob_service_client.get_container_client(container_name)


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}