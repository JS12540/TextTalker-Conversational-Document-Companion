import pandas as pd
from fastapi import UploadFile, HTTPException
import traceback
from io import BytesIO
from PyPDF2 import PdfReader
from docx import Document
import io
from io import StringIO

def process_text_file(file: UploadFile) -> str:
    print("Request received for Text file")
    text = ""
    with StringIO() as buffer:
        for chunk in iter(lambda: file.file.read(4096), b""):
            buffer.write(chunk.decode())
        buffer.seek(0)
        text = buffer.read()
    print(f"text : {text}")
    return text


async def process_uploaded_docx(file: UploadFile) -> str:
    print("Request received for Docx file")
    
    # Read the contents of the uploaded file
    contents = await file.read()
    
    # Wrap the bytes in a file-like object
    file_like = io.BytesIO(contents)

    doc = Document(file_like)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    
    print(f"Text : {text}")
    
    # Close the file-like object if necessary
    file_like.close()
    
    return text


async def process_pdf_file(file: UploadFile) -> str:
    try:
        print("Request received for PDF file")
        pdf_bytes = await file.read()
        text = ""
        with BytesIO(pdf_bytes) as file:
            reader = PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        traceback.print_exc()  # Print traceback for detailed error information
        raise HTTPException(status_code=500, detail="Error processing PDF file: " + str(e))

def process_csv_file(file: UploadFile) -> str:
    print("Request received for CSV file")
    df = pd.read_csv(file.file)
    text = df.to_string()
    print(f"Text : {text}")
    return text