import os
import json

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI


load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
CHROMA_PATH = 'chroma'


def get_embeddings():
    return OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY, model='text-embedding-3-small')


def add_doc(path):
    # Load PDF and split into chunks
    loader = PyPDFLoader(path)
    pages = loader.load_and_split()

    # Embed the chunks as vectors and load them into DB
    Chroma.from_documents(
        pages,
        get_embeddings(),
        collection_metadata={'hnsw:space': 'cosine'},
        persist_directory=CHROMA_PATH)


# add_doc('D:\\Downloads\\Cosmic Encounter.pdf')
question = 'what do defensive allies get when winning an encounter?'
model = ChatOpenAI(model='gpt-3.5-turbo', temperature=0)

res = model.invoke(f'''
    You are given this text: "{question}".

    Use it for these tasks, in order:
    - Translate to English and make concise.
    - Extract descriptive keywords.
    - Combine them into 1 keyword string.

    Then, return a JSON with 2 fields:
    - "lang": Detected language.
    - "keywords": Keyword string as a result from the tasks above.
''')
tokens = res.usage_metadata['total_tokens']
res_json = json.loads(res.content)
print('Conversion:', res_json)
lang = res_json.get('lang', 'English')
keywords = res_json.get('keywords', question)

db = Chroma(persist_directory=CHROMA_PATH, embedding_function=get_embeddings())
docs = db.similarity_search_with_relevance_scores(keywords, k=2)
print('Retrieval:', [doc.metadata['page'] + 1 for doc, _ in docs])
context = '\n---\n'.join([
    f'''
    (Page {doc.metadata['page'] + 1})

    {doc.page_content}
    '''
    for doc, _ in docs
])

res = model.invoke(f'''
    You will answer this question related to a board game: "{question}".
    Use this language: {lang}.

    Context is provided after triple backticks below.
    Do not share info outside of the context.
    Answer concisely and procedurally.
    Ensure conditions in the question matches the context to avoid mistakes.

    If context is found: summarize the relevant texts, then put the page number at the end, e.g., "(Page 1)".
    If the question is irrelevant or context is not found: politely refuse.
    ```
    {context}
''')
tokens += res.usage_metadata['total_tokens']

print(f'Q: {question}')
print(f'A: {res.content}')
print('Cost:', round(tokens / 1000000 * 0.5 * 16250))
