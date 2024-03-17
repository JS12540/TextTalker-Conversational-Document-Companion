import pandas as pd
from fastapi import UploadFile, HTTPException
import traceback
from io import BytesIO
from PyPDF2 import PdfReader
from docx import Document
import io
from io import StringIO

def process_text_file(file: UploadFile) -> str:
    """
    Process a text file and return its contents as a string.

    Args:
        file (UploadFile): The text file to be processed.

    Returns:
        str: The contents of the text file as a string.
    """
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
    """
    A function that processes an uploaded docx file by reading its contents, wrapping the bytes in a file-like object, extracting text from paragraphs, and returning the extracted text as a string.
    Parameters:
        file (UploadFile): The uploaded docx file to be processed.
    Returns:
        str: The extracted text from the docx file.
    """
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
    """
    A function that processes a PDF file uploaded through the API.

    Parameters:
    - file (UploadFile): The PDF file to be processed.

    Returns:
    - str: The extracted text content from the PDF file.
    """
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
    """
    A function that processes a CSV file, converting it to a string and returning the result.

    Parameters:
    file (UploadFile): The CSV file to be processed.

    Returns:
    str: The contents of the CSV file as a string.
    """
    print("Request received for CSV file")
    df = pd.read_csv(file.file)
    text = df.to_string()
    print(f"Text : {text}")
    return text