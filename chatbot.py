from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash",api_key=GOOGLE_API_KEY)

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001",google_api_key=GOOGLE_API_KEY)

text_splitter=RecursiveCharacterTextSplitter(chunk_size=100,chunk_overlap=0,separators=["\n \n"])

def chatbot_pipeline(knowledge_base_directory, question):

    question = question

    pdf_docs = [os.path.join(knowledge_base_directory, pdf) for pdf in os.listdir(knowledge_base_directory)]
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()

    splits = text_splitter.split_text(text)

    vectordb=FAISS.from_texts(texts=splits,embedding=embeddings)

    memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True)
    
    template = """Use the following pieces of context to answer the question at the end.Use the provided context to answer the question as accurately as possible. If you don't know the answer, just say that you don't know, don't try to make up an answer.Context is mostly about a second year IT undergraduate at University of Moratuwa, Srilanka, whoose name Hashiru Gunathilake.So Answer for the questions as Hashiru Gunathilake.Always say "thanks for asking!" at the end of the answer.
    {context}
    Question: {question}
    Helpful Answer:"""
    QA_CHAIN_PROMPT = PromptTemplate(input_variables=["context", "question"],template=template)


    
    qa_chain = RetrievalQA.from_chain_type(llm,
                                       retriever=vectordb.as_retriever(),
                                       return_source_documents=True,
                                       chain_type_kwargs={"prompt": QA_CHAIN_PROMPT})
    
    
    return qa_chain({"query": question})["result"]