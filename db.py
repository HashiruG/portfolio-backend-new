from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os


load_dotenv()

databaseURI = os.getenv("DATABASE_URI")
databaseName = os.getenv("DATABASE_NAME")


def getDatabase():
    client = AsyncIOMotorClient(databaseURI)
    return client[databaseName]

