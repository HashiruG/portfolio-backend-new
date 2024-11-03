from fastapi import FastAPI
from db import getDatabase
from motor.motor_asyncio import AsyncIOMotorClient
import os


database = getDatabase()


project_collection = database["projects"]
programming_skills_collection = database["programming_skills"]
web_skills_collection = database["web_skills"]
machine_learning_skills_collection = database["machine_learning_skills"]

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}