from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document
from persona import create_conversational_agent
from question_generator import quiz_generator
import os

API_KEY = "<insert key here>"
COLLECTION_NAME = "history_collection"

# llm for chat agent
llm = ChatOpenAI(
    model_name="llama3-70b-8192",
    openai_api_base="https://api.groq.com/openai/v1",
    openai_api_key=API_KEY,
    temperature=0.7,
    max_tokens=512
)

def db_path():
    this_folder = os.path.dirname(__file__)
    main_folder = os.path.abspath(os.path.join(this_folder, os.pardir))
    persist_directory = os.path.join(main_folder, "resources", "chromadb", "history_chroma")
    return persist_directory

def load_vector_db(persist_directory: str):

    embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_db = Chroma(
        persist_directory=persist_directory,
        embedding_function=embedder,
        collection_name=COLLECTION_NAME
    )
    return vector_db


vector_db = load_vector_db(db_path())

#call the chat agent
agent = create_conversational_agent(llm, vector_db)

def generate_quiz_data():

    all_docs = vector_db.get(include=["documents"])["documents"]
    docs = [Document(page_content=chunk) for chunk in all_docs]

    # llm for quiz generation
    llm_quiz = ChatOpenAI(
        model_name="llama3-70b-8192",
        openai_api_base="https://api.groq.com/openai/v1",
        openai_api_key=API_KEY,
        temperature=0.0,
        max_tokens=1000
    )
    # return questions to the ui
    mcq_questions, short_questions = quiz_generator(llm_quiz, docs)
    return mcq_questions, short_questions