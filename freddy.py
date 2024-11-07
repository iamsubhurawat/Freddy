import os
import requests

from dotenv                               import load_dotenv
from deepgram                             import Deepgram
from langchain_groq                       import ChatGroq
from langchain.chains                     import RetrievalQA
from langchain_community.embeddings       import HuggingFaceEmbeddings
from langchain_community.vectorstores     import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_experimental.text_splitter import SemanticChunker

load_dotenv()

groq_api     = os.getenv("GROQ_API_KEY")
deepgram_api = os.getenv("DEEPGRAM_API_KEY")

dg = Deepgram(deepgram_api)
params = {
"punctuate": True,
"model": "general",
"tier": "nova"
}

url = "https://api.deepgram.com/v1/speak?model=aura-asteria-en"
headers = {
    "Authorization": f"Token {deepgram_api}",
    "Content-Type": "application/json"
}

embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
text_splitter = SemanticChunker(embedding_model, breakpoint_threshold_type="percentile")

llm = ChatGroq(temperature=0, groq_api_key=groq_api, model_name="mixtral-8x7b-32768")

def speech_to_text(audio):
    with open(audio,"rb") as f:
        source = {"buffer": f, "mimetype": "audio/"+"wav"}
        res = dg.transcription.sync_prerecorded(source,params)
    transcribed_text = res['results']['channels'][0]['alternatives'][0]['transcript']
    return transcribed_text

def creating_vectordb(pdf_file):
    loader = PyPDFLoader(pdf_file)
    data = loader.load_and_split()
    docs = text_splitter.split_documents(data)
    vectordb = FAISS.from_documents(docs, embedding_model)
    return vectordb

def creating_retrieval_chain(db):
    retriever = db.as_retriever()
    qa = RetrievalQA.from_llm(llm=llm,retriever=retriever)
    return qa

def groq_response(qa,user_input):
    result = qa.invoke({"query": user_input})
    response = result["result"]
    return response

def text_to_speech(text,path):
    payload = {
        "text": text
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        with open(path, "wb") as f:
            f.write(response.content)
        return 1
    else:
        print(f"Error: {response.status_code} - {response.text}")