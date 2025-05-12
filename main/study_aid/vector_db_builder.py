import os
from PyPDF2 import PdfReader
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings

def getPath() -> str:
    # Path to the folder containing this script (i.e., .../main/somefolder)
    this_folder = os.path.dirname(__file__)
    # Go up one directory to reach .../main
    main_folder = os.path.abspath(os.path.join(this_folder, os.pardir))
    # Then go into resources/History-1.pdf
    resource_path = os.path.join(main_folder, "resources", "History-1.pdf")
    return resource_path

def extract_pdf_text(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    pages  = [p.extract_text() or "" for p in reader.pages]
    return "\n".join(pages)

# Split into overlapping chunks
def split_text(text: str, chunk_size=6000, chunk_overlap=400):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return [Document(page_content=chunk) for chunk in splitter.split_text(text)]

def save_to_vector_db(docs, persist_directory: str, collection_name: str):
    embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectordb = Chroma.from_documents(
        documents=docs, embedding=embedder, persist_directory=persist_directory,
        collection_name=collection_name
    )

    return vectordb

def main():
    collection_name = "history_collection"
    this_folder = os.path.dirname(__file__)
    main_folder = os.path.abspath(os.path.join(this_folder, os.pardir))
    persist_directory = os.path.join(main_folder, "resources", "chromadb", "history_chroma")

    pdf_path = getPath()

    # 1) Extract
    text = extract_pdf_text(pdf_path)
    docs = split_text(text)
    vectordb = save_to_vector_db(docs, persist_directory, collection_name)


if __name__ == "__main__":
    main()
