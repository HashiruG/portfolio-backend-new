from fastapi import FastAPI, UploadFile, Form, File,HTTPException
from db import getDatabase
from azure.storage.blob import BlobServiceClient
from azure.storage.blob import ContentSettings
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
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


class Project(BaseModel):
    name: str
    description: str
    image_url: str

class Skill(BaseModel):
    skillName: str
    skillURL: str
    category: str


app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173/"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"]
)

#projects routes

@app.get("/projects", response_model=List[Project])
async def get_projects():
    projects = []
    
    async for project in project_collection.find():
        projects.append(project)
        print(projects)
    return projects


@app.post("/projects")
async def create_project(
    name: str = Form(...),
    description: str = Form(...),
    image: UploadFile = File(...)
):

    content_type = image.content_type

    try:
        #upload image to blob storage
        blob_client = container_client.get_blob_client(image.filename)
        
        blob_client.upload_blob(
            image.file, 
            content_settings=ContentSettings(content_type=content_type)
        )

       #Save project details to database
        project = {
            "name": name,
            "description": description,
            "image_url": f"https://portimagesforweb.blob.core.windows.net/{container_name}/{image.filename}",
        }
        await project_collection.insert_one(project)

        return {"message": "Project created successfully"}

    except Exception as e:
        return {"error": str(e)}


#skills routes
@app.get("/programming_skills")
async def get_projects():
    programming_skills = []
    programming_skill["_id"] = str(programming_skill["_id"])
    async for programming_skill in programming_skills_collection.find():
        programming_skills.append(programming_skill)
        print(programming_skills)
    return programming_skills


@app.get("/web")
async def get_projects():
    web_skills = []
    web_skill["_id"] = str(web_skill["_id"])
    async for web_skill in web_skills_collection.find():
        web_skills.append(web_skill)
        print(web_skills)
    return web_skills    


@app.get("/ml")
async def get_projects():
    ml_skills = []
    ml_skill["_id"] = str(ml_skill["_id"])
    async for ml_skill in machine_learning_skills_collection.find():
        ml_skills.append(ml_skill)
        print(ml_skills)
    return ml_skills   


@app.post("/skills")
async def add_skill(skill: Skill):

    if skill.category.lower() == "programming":
        collection = programming_skills_collection
    elif skill.category.lower() == "web development":
        collection = web_skills_collection
    elif skill.category.lower() == "machine learning":
        collection = machine_learning_skills_collection
    else:
        raise HTTPException(status_code=400, detail="Invalid category specified.")


    await collection.insert_one(skill.dict())
    return {"message": "Skill added successfully!"}



