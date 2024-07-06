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
question = 'kita jadi siapa di game ini?'
model = ChatOpenAI(model='gpt-3.5-turbo', temperature=0)

res = model.invoke(f'''
    You are given this input: "{question}".
    Return a JSON with 2 fields:
    - "lang": detected language (most likely English or Indonesian)
    - "en": text translated to English, abbreviations expanded
''')
res_json = json.loads(res.content)
question_lang = res_json.get('lang', 'English')
question_en = res_json.get('en', question)
print('First pass:', res_json)
tokens = res.usage_metadata['total_tokens']

db = Chroma(persist_directory=CHROMA_PATH, embedding_function=get_embeddings())
docs = db.similarity_search_with_relevance_scores(question_en, k=2)
print('Pages fetched:', [doc.metadata['page'] + 1 for doc, _ in docs])
context = '\n---\n'.join([
    f'''
    (Page {doc.metadata["page"] + 1})

    {doc.page_content}
    '''
    for doc, _ in docs
])

res = model.invoke(f'''
    You will answer this question related to a board game: "{question}".
    Use this language: {question_lang}.

    Context is provided after triple backticks below.
    Do not share info outside of the context.
    Do not preface your response.
    Ensure specific conditions in the question matches the context.

    If context is found: summarize the most relevant texts, then put the page number at the end, e.g., "(Page 1)".
    If the question is irrelevant or context is not found: politely refuse.
    ```
    {context}
''')
tokens += res.usage_metadata['total_tokens']
answer = res.content

print(f'Q: {question}')
print(f'A: {answer}')
print(f'(Rp{round(tokens / 1000000 * 0.5 * 16250)})')
