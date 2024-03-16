from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any
import os
import pymongo
import services
import constants
import traceback
import embeddings
import os
import constants

os.environ["OPENAI_API_KEY"] = constants.API_KEY

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000"
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB configuration
MONGO_URI = constants.MONGODB_URL
if not MONGO_URI:
    raise ValueError("MongoDB URI not found in environment variables.")
mongo_client = pymongo.MongoClient(MONGO_URI)
db = mongo_client["file_storage"]

# ML Model (dummy for demonstration)
def predict(text: str) -> str:
    # Implement your machine learning model logic here
    return "dummy prediction"



async def process_uploaded_file(file: UploadFile) -> str:
    extension = os.path.splitext(file.filename)[1].lower()

    try:
        if extension == '.txt':
            text = services.process_text_file(file)
        elif extension == '.docx':
            text = await services.process_uploaded_docx(file)
        elif extension == '.pdf':
            text = await services.process_pdf_file(file)
        elif extension == '.csv':
            text = services.process_csv_file(file)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format.")

        return text
    except HTTPException:
        raise  # Re-raise HTTPException to maintain original status code and detail
    except Exception as e:
        traceback.print_exc()  # Print traceback for detailed error information
        raise HTTPException(status_code=500, detail="Error processing file: " + str(e))


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> Any:
    # Save the file to MongoDB

    collection = db["files"]

    existing_file = collection.find_one({"filename": file.filename})
    if existing_file:
        return {"result": "File already exists."}

    inserted_file = collection.insert_one({"filename": file.filename, "filetype": file.content_type})

    text = await process_uploaded_file(file)

    model = embeddings.create_embeddings(text)

    return {"result": "File uploaded successfully."}


@app.post("/predict")
async def query_file(query: str):

    result = embeddings.query(query)

    return {"result": result}
