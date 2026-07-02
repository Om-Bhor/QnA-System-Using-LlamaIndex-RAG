import os
import pdfplumber
import pypdfium2 as pyfium
import chromadb
import time
from docx import Document
from pptx import Presentation
from IPython.display import display,Markdown
from PIL import Image
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)

db_client = chromadb.PersistentClient(
    path= "./Chroma_db"
)

try:
    collection = db_client.get_collection(
        name = "multimodal_rag"
    )
    print("collection loaded")
except:
    collection = db_client.create_collection(
        name="multimodal_rag"
    )
    print("collection created")

def extract_docx(file_path):
    doc = Document(file_path)
    text =""
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            text += paragraph.text + "\n"
    return text

def get_processed_files(collection):
    results =collection.get()
    processed_files = set()
    for metadata in results["metadatas"]:
        processed_files.add(
            metadata["source"]
        )
    return processed_files

def load_document(file_path):
    extension = os.path.splitext(file_path)[1].lower()
    documents = []
    if extension ==".txt":
        with open(file_path,"r",encoding="utf-8") as file:
            text =file.read()
        if text.strip():
            documents.append(
                {
                    "content":text,
                    "type":"text"
                }
            )
    
    elif extension ==".pdf":
        text =""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
            
                if page_text:
                    text += page_text+ "\n"
        text = text.replace("\u2028", "\n")
        text = text.replace("\u2029", "\n")
        if text.strip():
            documents.append(
                {
                    "content":text,
                    "type":"text"
                }
            )
    # elif extension == ".pptx":
    #     ppt_documents = extract_pptx(file_path)
    #     documents.extend(ppt_documents)
    elif extension == ".docx":
        text = extract_docx(file_path)
        documents.append(
            {
                "content":text,
                "type": "text"
            }
        )
    else:
        print(f"Skipping Unsupported file {file_path} {extension}")
    return documents

def chunk_text(text,chunk_size=1000,overlap=200):
    chunks = []
    start =0
    while start<len(text):
        end = start+chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def create_embedding(text):
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents = text
    )
    return response.embeddings[0].values

def store_embeddings(new_chunks):
    for chunk in new_chunks:
        embedding = create_embedding(chunk["content"])
        collection.add(
            ids = [f"{chunk['source']}_{chunk['chunk_id']}"],
            documents = [chunk["content"]],
            embeddings = [embedding],
            metadatas=[
                {
                    "source" : chunk["source"],
                    "chunk_id" :chunk["chunk_id"],
                    "type": chunk["type"]
                }
            ]
        )
    print("stored successfully")
def load_new_folder(folder_path,collection):
    processed_files= get_processed_files(collection)
    all_chunks = []
    for file in os.listdir(folder_path):
        if file in processed_files:
            print(f"Skipping {file} (already embedded andstored)")
            continue
        file_path = os.path.join(
            folder_path,
            file
        )
        print(f"Reading file {file}")
        
        documents = load_document(file_path)
        for doc in documents:
            chunks = chunk_text(doc["content"])
            for i,chunk in enumerate(chunks):
                all_chunks.append(
                    {
                        "source":file,
                        "chunk_id": i,
                        "content": chunk,
                        "type":doc["type"]
                    }
                )
        print(f"Loaded{file}")
    store_embeddings(all_chunks)

# load_new_folder("../Data",collection)

def retrieve_chunks(query):
    query_embedding = create_embedding(query)
    results = collection.query(
        query_embeddings =[query_embedding],
        n_results = 3
    )
    return results

def build_context(results):
    context = ""
    for doc in results["documents"][0]:
        context += doc
        context += "\n\n"
    return context

def classify_query(query):
    query = query.lower()
    academic_keywords = [
        "assignment",
        "mcq",
        "summary",
        "notes",
        "exam",
        "question",
        "important question",
        "interview",
        "placement",
        "career",
        "roadmap",
        "project",
        "python",
        "java",
        "sql",
        "javascript",
        "machine learning",
        "deep learning",
        "ai",
        "artificial intelligence",
        "rag",
        "llm",
        "agent",
        "dsa",
        "data structure",
        "algorithm",
        "resume",
        "operating system",
        "dbms",
        "computer network",
        "aptitude",
        "coding"
    ]
    blocked_keywords = [
        "who is",
        "stock",
        "share market",
        "crypto",
        "bitcoin",
        "politics",
        "election",
        "prime minister",
        "president",
        "movie",
        "actor",
        "actress",
        "celebrity",
        "ipl",
        "football",
        "cricket",
        "weather",
        "news"
    ]
    for keyword in blocked_keywords:
        if keyword in query:
            return "non-academic"
    # for keyword in academic_keywords:
    #     if keyword in query:
    #         return "academic"
    return "academic"



def detect_intent(question):
    question = question.lower()
    if "mcq" in question or "multiple choice questions" in question:
        return "mcq"
    elif "summary" in question or "summarize" in question:
        return "summary"
    elif "imp question" in question or "important question" in question:
        return "important_question"
    elif "solve" in question or "assignment" in question:
        return "assignment"
    elif "interview" in question or "viva" in question:
        return "interview_prep"
    elif "placement" in question or "off-campus" in question:
        return "placement_prep"
    elif "roadmap" in question or "career" in question :
        return "career_guidance"
    elif "project idea" in question or "project ideas" in question or "project" in question :
        return "project_idea"
    else:
        return "explanation"

def create_prompt(intent, context, question,retrieval_found):
    if retrieval_found:
        source_instruction = f"""
        Use the provided study material as the PRIMARY source.

        If the answer exists in the study material,
        answer using the study material.

        Do not ignore the provided context.

        Study Material:
        {context}
        """
    else:
        source_instruction = """
        No relevant study material was found.

        Answer using your academic knowledge.

        You may answer ONLY questions related to:

        - Academic subjects
        - Assignments
        - Exams
        - Interview preparation
        - Placement preparation
        - Career guidance
        - Programming
        - Artificial Intelligence
        - Machine Learning
        - Data Structures & Algorithms
        - Project ideas

        Do NOT answer:

        - Politics
        - News
        - Stock market
        - Cryptocurrency
        - Sports
        - Entertainment
        - Celebrity topics
        """
    if intent == "mcq":

        return f"""
            You are an AI Academic Assistant.

            Using ONLY the provided context,
            generate 10 MCQs.

            For each MCQ provide:

            1. Question
            2. Four Options
            3. Correct Answer
            4. Explanation

            Context:
            {source_instruction}

            Student Request:
            {question}
            """

    elif intent == "summary":

        return f"""
            You are an AI Academic Assistant.

            Create concise exam notes.

            Include:

            - Key Concepts
            - Important Definitions
            - Important Points

            Context:
            {source_instruction}

            Student Request:
            {question}
            """

    elif intent == "important_questions":

        return f"""
            You are an AI Academic Assistant.

            Generate likely university exam questions.

            Provide:

            - 2 Marks Questions
            - 5 Marks Questions
            - 10 Marks Questions

            Context:
            {source_instruction}

            Student Request:
            {question}
            """
    elif intent == "assignment":

        return f"""
            You are an AI Academic Assistant.

            Solve the assignment question step by step.

            Use only the provided context.

            Context:
            {source_instruction}

            Student Request:
            {question}
            """
    elif intent == "interview_prep":

        return f"""
        You are an AI Academic Assistant.

        Help the student prepare for interviews.

        Include:

        - Important concepts to study
        - Common interview questions
        - Preparation strategy
        - Mistakes to avoid

        Student Question:
        {question}
        """
    elif intent == "placement_prep":

        return f"""
        You are an AI Academic Assistant.

        Help the student prepare for placements.

        Include:

        - Preparation roadmap
        - Important skills
        - Aptitude preparation
        - Technical preparation
        - Interview preparation tips

        Student Question:
        {question}
        """
    elif intent == "career_guidance":

        return f"""
        You are an AI Academic Assistant.

        Provide a structured career roadmap.

        Include:

        - Skills to learn
        - Technologies to focus on
        - Projects to build
        - Resources
        - Career opportunities

        Student Question:
        {question}
        """
    elif intent == "project_idea":

        return f"""
        You are an AI Academic Assistant.

        Suggest practical project ideas.

        For each project provide:

        - Project Title
        - Difficulty Level
        - Tech Stack
        - Features
        - Learning Outcomes

        Student Question:
        {question}
        """
    else:

        return f"""
            You are an AI Academic Assistant.

            Explain clearly in simple student-friendly language.

            Context:
            {source_instruction}

            Student Question:
            {question}
            """

SIMILARITY_THRESHOLD = 1.2
def validate_retrieval(results):
    if not results:
        return False
    documents = results.get("documents", [])
    distances = results.get("distances", [])
    if not documents or not documents[0]:
        return False
    if not distances or not distances[0]:
        return False
    best_distance = distances[0][0]
    return best_distance <= SIMILARITY_THRESHOLD

def ask_question(query):
    query_type = classify_query(query)
    if query_type =="non-academic":
        return {
        "answer":
        """
        This assistant is designed only for
        academic learning, placement preparation,
        interview preparation and career guidance.

        Please ask an academic-related question.
        """,
        "sources":[]
        }
    results = retrieve_chunks(query)
    retrieval_found = validate_retrieval(results)
    if retrieval_found:
        context = build_context(results)
        metadata = results["metadatas"][0]
    else:
        context = ""
        metadata = []
    intent = detect_intent(query)
    # Step 5: Create prompt
    prompt = create_prompt(
        intent,context,query,retrieval_found
    ) 
    # Step 6: Generate answer
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    sources = []
    for item in metadata:
        sources.append(
            f"{item['source']} (Chunk {item['chunk_id']})"
        )
    return {
        "answer":response.text,
        "sources": sources
        }


# query = input("\nEnter a Question:")
# if query.lower()== "exit":
#     break
# Answer = ask_question(query)
# display(Markdown(Answer["answer"]))
# print("\nSources:")

# for source in Answer["sources"]:
#     print("-", source)

 
def process_file(file_path):
    file_name = os.path.basename(file_path)
    existing_files = get_processed_files(collection)
    if file_name in existing_files:
        print(f"{file_name} File is already embedded")
        return
    documents = load_document(file_path)
    chunks_to_store=[]
    for doc in documents:
        chunks = chunk_text(doc["content"])
        for i, chunk in enumerate(chunks):
            chunks_to_store.append(
                    {
                        "source":file_name,
                        "chunk_id": i,
                        "content": chunk,
                        "type":doc["type"]
                    }
                )
    store_embeddings(chunks_to_store)
    print(f"{file_name} Loaded Successfully")
