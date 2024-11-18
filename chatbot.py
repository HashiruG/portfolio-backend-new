from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
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

r_splitter = RecursiveCharacterTextSplitter(chunk_size=100,chunk_overlap=0,separators=["\n \n"])

def chatbot_pipeline(knowledge_base_directory, question):

    question = question
    

    loader = PyPDFLoader(knowledge_base_directory)
    pages = loader.load()

    splits = r_splitter.split_documents(pages)
    print("splits done \n")
    print(splits)

    vectordb = Chroma.from_documents(
    documents=splits,
    embedding=embeddings,
    persist_directory="./db/chroma")


    memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True)
    
    template = """Use the following pieces of context to answer the question at the end. Basically questions should be about an undergraduate individual of university of Moratuwa Srilanka. If you don't know the answer, just say that you don't know, don't try to make up an answer.Always say "thanks for asking!" at the end of the answer.
    {context}
    Question: {question}
    Helpful Answer:"""
    QA_CHAIN_PROMPT = PromptTemplate(input_variables=["context", "question"],template=template)


    
    qa_chain = RetrievalQA.from_chain_type(llm,
                                       retriever=vectordb.as_retriever(),
                                       return_source_documents=True,
                                       chain_type_kwargs={"prompt": QA_CHAIN_PROMPT})
    
    
    return qa_chain({"query": question})["result"]