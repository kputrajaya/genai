import os

from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate


load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
CHROMA_PATH = 'chroma'


def get_embeddings():
    return OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY, model='text-embedding-3-small')


def add_doc(path):
    # Load PDF and split into chunks
    loader = PyPDFLoader(path)
    pages = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(pages)

    # Embed the chunks as vectors and load them into DB
    Chroma.from_documents(chunks, get_embeddings(), persist_directory=CHROMA_PATH)


def load_db():
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=get_embeddings())
    return db


# add_doc('D:\\Downloads\\Games\\Cosmic Encounter.pdf')
db = load_db()

query = 'during encounter, what if both attacker and defender use negotiation cards?'
docs_chroma = db.similarity_search_with_score(query, k=5)
context_text = '\n\n'.join([doc.page_content for doc, _ in docs_chroma])

prompt = ChatPromptTemplate.from_template('''
    Answer this question using only the context after triple backticks: {question}.
    Do not give info not mentioned in the context.
    ```
    {context}
''').format(context=context_text, question=query)
model = ChatOpenAI(model='gpt-3.5-turbo')
response_text = model.invoke(prompt).content
print(response_text)
