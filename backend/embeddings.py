from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain_community.vectorstores import Chroma
from constants import OPENAI_API_KEY
import os

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

class AIAssistant:
    def __init__(self):
        self.llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
        self.retriever = None
        self.model = None

    def create_embeddings(self, text):
        """
        Split text into chunks, generate embeddings, and set up retriever and model for retrieval question answering.

        Parameters:
            text (str): The input text to generate embeddings from.

        Returns:
            None
        """
        # Split text into chunks
        text_splitter = CharacterTextSplitter(        
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        texts = text_splitter.create_documents([text])

        ids = [str(i) for i in range(1, len(texts) + 1)]

        print(f"Text : {texts[0]}")

        if not texts:
            raise ValueError("Text chunks are empty")

        # Generate embeddings
        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)  # Assuming OPENAI_API_KEY is defined
        vectorstore = Chroma.from_documents(documents=texts, embedding=embeddings, ids=ids)

        # Retrieve and generate using the relevant snippets
        self.retriever = vectorstore.as_retriever(search_type="similarity")

        self.model = RetrievalQA.from_chain_type(
            self.llm,
            retriever=self.retriever,
            chain_type="stuff"
        )

    def query(self, question: str):
        """
        Query the model with a given question and return the response.

        Parameters:
            question (str): the question to query the model with.

        Returns:
            The response from the model.
        """
        if not self.model:
            raise ValueError("Model not initialized. Call create_embeddings() first.")
        response = self.model.run(question)
        return response
    
