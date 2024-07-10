import os
import langchain
import PyPDF2
from langchain.vectorstores.faiss import FAISS
from langchain.chat_models import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.chains import RetrievalQAWithSourcesChain
from PyPDF2.errors import PdfReadError 
from clean import folder_cleaner
def initialize_embeddings(model_name="BAAI/bge-base-en-v1.5", device='cpu'):
    hfembeddings=HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': device}
    )
    return hfembeddings

def extract_text_from_pdf(data_dir_path):
    docs=[]
        
    dir_loader=DirectoryLoader(
        data_dir_path,
        glob='*.pdf',
        loader_cls=PyPDFLoader
    )
    
    docs = []
    for file_path in dir_loader.load():
        try:
            docs.append(file_path)
        except PyPDF2.errors.EmptyFileError:  
                continue
        except PyPDF2.utils.PdfReadError:
                continue
    
    print("PDFs Loaded")
    return docs

def load_vector_db(vector_db_path, embeddings,folder_path,docs):
    try:
        vectordb=FAISS.load_local(vector_db_path, embeddings, allow_dangerous_deserialization=True)
        return vectordb
    except:
        hfembeddings=initialize_embeddings()
        # docs=extract_text_from_pdf(folder_path)
        db=FAISS.from_documents(documents=docs, embedding=hfembeddings)
        db.save_local(vector_db_path)
        vectordb=FAISS.load_local(vector_db_path, embeddings, allow_dangerous_deserialization=True)
        return vectordb


def initialize_llm(api_key, temperature=0.8, max_tokens=500, model_name="gpt-3.5-turbo"):
    os.environ['OPENAI_API_KEY'] = api_key
    llm=ChatOpenAI(temperature=temperature, max_tokens=max_tokens, model_name=model_name)
    return llm

def create_retrieval_chain(llm, vectordb):
    chain=RetrievalQAWithSourcesChain.from_llm(llm=llm, retriever=vectordb.as_retriever())
    return chain

def query_resumes(chain, query):
    prompt = f'''
    You are an AI bot designed to act as a professional for parsing resumes and matching them with job descriptions. 
    You are given a resume and a job description. Your tasks are:
    
    1. Match the multiple resumes with the job description and determine how well it fits.
    2. Provide a match score between 0 to 100, where 100 means a perfect fit.
    3. Indicate whether the resumes which are good fit for the job with a "yes" or "no",
     for the documents for which your answer is 'Yes' give the name of the documents as output.
    
    Job Description: {query}
    '''
    result=chain({'question': prompt})
    return result

def parser(folder_path, query):
    folder_cleaner(folder_path)
    vector_db_path=r"faiss/parser"
    api_key='your api key'
    embeddings=initialize_embeddings()
    docs=extract_text_from_pdf(folder_path)
    vectordb=load_vector_db(vector_db_path, embeddings,folder_path,docs)
    llm=initialize_llm(api_key)
    chain=create_retrieval_chain(llm, vectordb)
        
    result=query_resumes(chain, query)
        
    return result['sources']

   
# if __name__ == "__main__":
#     main()
