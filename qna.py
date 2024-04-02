import google.generativeai as genai
from langchain import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os


load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


if not GOOGLE_API_KEY:
    raise ValueError("Google API Key not found in environment variables.")

genai.configure(api_key=GOOGLE_API_KEY)
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
combined_content = ""

with open('./data/Attractions.txt', 'r') as file:
    attractions_content = file.read()
    combined_content += attractions_content + "\n\n"  # Add a newline for separation

# Load the Ooty Hotels Facilities file as text
with open('./data/ooty_hotels_facilities_enhanced_data_updated.txt', 'r') as file:
    hotels_content = file.read()
    combined_content += hotels_content

# Process the combined content
data = combined_content
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
texts = text_splitter.split_text(data)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
vector_store = Chroma.from_texts(texts, embeddings).as_retriever()

prompt_template = """
  Please answer the question in as much detail as possible based on the provided context.
  Ensure to include all relevant details. If the answer is not available in the provided context,
  kindly respond with "The answer is not available in the context." Please avoid providing incorrect answers.
\n\n
  Context:\n {context}?\n
  Question: \n{question}\n

  Answer:
"""

prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
from langchain_google_genai import ChatGoogleGenerativeAI
model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

question = input("Enter your question: ")
docs = vector_store.get_relevant_documents(question)

response = chain({"input_documents": docs, "question": question}, return_only_outputs=True)
print(response)
