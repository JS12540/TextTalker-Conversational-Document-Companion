import pandas as pd
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain import hub
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain_community.vectorstores import Chroma
from constants import API_KEY
import os

os.environ["OPENAI_API_KEY"] = API_KEY

llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

retriever = None

def create_embeddings(text):
    global retriever, model

    # Split text into chunks
    text_splitter = CharacterTextSplitter(        
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    texts = text_splitter.create_documents([text])

    print(f"Text : {texts[0]}")

    if not texts:
        raise ValueError("Text chunks are empty")

    # Generate embeddings
    embeddings = OpenAIEmbeddings(openai_api_key=API_KEY)  # Assuming OPENAI_API_KEY is defined
    vectorstore = Chroma.from_documents(documents=texts, embedding=embeddings)

    # Retrieve and generate using the relevant snippets
    retriever = vectorstore.as_retriever(search_type="similarity")

    model = RetrievalQA.from_chain_type(
        llm,
        retriever=retriever,
         chain_type="stuff"
        )

    return retriever

def query(question: str):
    global model
    response = model.run(question)
    return response