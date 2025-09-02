import os
from fastapi import FastAPI
from pydantic import BaseModel
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import pipeline

# --- Global Variables ---
# We will load the models and build the index on startup
vector_store = None
qa_pipeline = None
runbooks_path = "/data/runbooks"

# --- FastAPI App Initialization ---
app = FastAPI(title="Document QA Service")

@app.on_event("startup")
def startup_event():
    """
    On startup, load models and build the document index.
    This is a one-time process.
    """
    global vector_store, qa_pipeline

    print("--- Loading models and building index ---")

    # 1. Load the embedding model
    print("Loading embedding model...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # 2. Load the runbook documents from the /data/runbooks directory
    print(f"Loading documents from {runbooks_path}...")
    loader = DirectoryLoader(runbooks_path, glob="**/*.md", show_progress=True)
    documents = loader.load()

    # 3. Split documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)

    # 4. Create the FAISS vector store (the index) from the chunks
    print("Creating FAISS vector store...")
    vector_store = FAISS.from_documents(texts, embeddings)
    print("--- Index is ready ---")

    # 5. Load the Question-Answering pipeline
    print("Loading QA pipeline...")
    qa_pipeline = pipeline(
        "question-answering", 
        model="deepset/roberta-base-squad2", 
        tokenizer="deepset/roberta-base-squad2",
        device="cuda:0"
    )
    print("--- QA pipeline is ready ---")


# --- API Endpoints ---
class QARequest(BaseModel):
    query: str
    top_k: int = 3 # Number of relevant chunks to retrieve

class QAResponse(BaseModel):
    answer: str
    score: float
    source: str

@app.post("/ask", response_model=QAResponse)
def ask(request: QARequest):
    """
    Accepts a question, finds relevant documents, and extracts an answer.
    """
    if not qa_pipeline or not vector_store:
        return {"error": "Models not loaded yet"}, 503

    # 1. Retrieve relevant documents from the vector store
    retriever = vector_store.as_retriever(search_kwargs={"k": request.top_k})
    docs = retriever.get_relevant_documents(request.query)

    # 2. Concatenate the context from the retrieved documents
    context = " ".join([doc.page_content for doc in docs])

    # 3. Use the QA pipeline to find the answer within the context
    result = qa_pipeline(question=request.query, context=context)

    return {
        "answer": result['answer'],
        "score": result['score'],
        "source": docs[0].metadata.get('source', 'Unknown') # Return the top source
    }

@app.get("/healthz")
def healthz():
    return {"status": "ok" if qa_pipeline and vector_store else "loading"}