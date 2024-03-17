from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any
import os
import pymongo
import traceback
from embeddings import AIAssistant  # Assuming AIAssistant class is imported correctly
import services
import constants

os.environ["OPENAI_API_KEY"] = constants.OPENAI_API_KEY

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

ai_assistant = None


async def process_uploaded_file(file: UploadFile) -> str:
    """
    A function that processes an uploaded file based on its extension.
    
    Parameters:
    - file: UploadFile - the file to be processed
    
    Returns:
    - str: the processed text content of the file
    """
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
    """
    Uploads a file to the server and processes it.

    Parameters:
        file (UploadFile): The file to be uploaded.

    Returns:
        Any: The result of the file upload operation.
    """
    extension = os.path.splitext(file.filename)[1].lower()

    if extension not in [".txt", ".docx", ".pdf", ".csv"]:
        return {"result": "Unsupported file format."}
    # Save the file to MongoDB
    global ai_assistant
    ai_assistant = None
    collection = db["files"]
    ai_assistant = AIAssistant()
    existing_file = collection.find_one({"filename": file.filename})
    if existing_file:
        text = existing_file['text']
        ai_assistant.create_embeddings(text)
        return {"result": "File already exists. Processing the existing file."}

    text = await process_uploaded_file(file)

    inserted_file = collection.insert_one({"filename": file.filename, "filetype": file.content_type, "text": text})

    ai_assistant.create_embeddings(text)

    return {"result": "File uploaded successfully."}


@app.post("/predict")
async def query_file(query: str):
    """
    Perform a prediction based on the provided query using the AI assistant.

    Parameters:
    - query (str): The query string to be used for prediction.

    Returns:
    - dict: A dictionary containing the result of the prediction.
    """
    global ai_assistant
    result = ai_assistant.query(query)

    return {"result": result}
