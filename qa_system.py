import os
import json
import numpy as np
import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, PDFFile, PDFEmbedding, Question, Answer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

# Initialize Rich console
console = Console()

# Load environment variables
load_dotenv()

# Database configuration
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

# AI API configuration
EMBEDDING_API_URL = os.getenv('AI_API_URL')
EMBEDDING_MODEL = os.getenv('AI_MODEL')
QA_API_URL = os.getenv('QA_API_URL')
QA_MODEL = os.getenv('QA_MODEL')
POD_API_KEY = os.getenv('POD_API_KEY')

# Create database connection - with error handling
try:
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    print("Database connection established")
except Exception as e:
    print(f"Database connection error: {e}")
    engine = None
    Session = None

# Simple fallback responses
fallback_responses = [
    "I'm not sure I understand. Could you rephrase your question?",
    "I don't have information about that yet. Is there something else I can help with?",
    "That's an interesting question, but I don't have a specific answer for it.",
    "I'm still learning and don't have an answer for that question yet."
]

def get_embedding(text, context=None):
    """Get embedding from the AI API with optional context."""
    try:
        input_text = text
        if context:
            input_text = f"{context}: {text}"
            
        response = requests.post(
            EMBEDDING_API_URL,
            headers={"Content-Type": "application/json"},
            json={
                "model": EMBEDDING_MODEL,
                "input": input_text
            }
        )
        response.raise_for_status()
        return response.json()['data'][0]['embedding']
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return None

def cosine_similarity(a, b):
    """Calculate cosine similarity between two vectors."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def search_similar_content(query, limit=5):
    """Search for similar content in the database."""
    if Session is None:
        return []
        
    try:
        session = Session()
        
        # Get query embedding
        query_embedding = get_embedding(query)
        if not query_embedding:
            return []
        
        # Get all embeddings from database
        results = session.query(PDFEmbedding, PDFFile).join(PDFFile).all()
        
        # Calculate similarities
        similarities = []
        for result in results:
            embedding = result.PDFEmbedding.embedding
            if embedding:
                similarity = cosine_similarity(
                    np.array(query_embedding),
                    np.array(embedding)
                )
                
                similarities.append({
                    'similarity': similarity,
                    'content': result.PDFEmbedding.page_content,
                    'file_name': result.PDFFile.filename,
                    'page_number': result.PDFEmbedding.page_number,
                    'metadata': {
                        'file_name': result.PDFFile.filename,
                        'page': result.PDFEmbedding.page_number,
                        'type': result.PDFEmbedding.content_type.value if result.PDFEmbedding.content_type else 'unknown',
                        'level': result.PDFEmbedding.hierarchy_level.value if result.PDFEmbedding.hierarchy_level else 'unknown'
                    }
                })
        
        # Sort by similarity
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:limit]
                
    except Exception as e:
        print(f"Error searching: {e}")
        return []
    finally:
        if session:
            session.close()

def get_llm_response(query, context_docs):
    """Get response from LLM using the context."""
    try:
        # Prepare context
        context = "\n\n".join([
            f"Document: {doc['file_name']} (Page {doc['page_number']})\n{doc['content']}"
            for doc in context_docs
        ])
        
        # Prepare messages for the LLM
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a Prop Firm Specialist providing information about our proprietary trading firm. "
                    "Format your responses for easy reading:\n\n"
                    "1. Use short paragraphs (2-3 sentences)\n"
                    "2. Use bullet points (with '- ' prefix) for lists\n"
                    "3. Use numbered lists (with '1. ' format) for steps\n"
                    "4. Add a blank line between paragraphs\n"
                    "5. Use headings that end with a colon\n"
                    "6. Keep responses under 300 words\n"
                    "7. Be direct and concise\n"
                    "8. Use simple formatting only (no tables or complex formatting)"
                )
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer the question based on the context. Format your response with paragraphs separated by blank lines, and use bullet points for lists."
            }
        ]

        # Call the LLM API with corrected endpoint
        response = requests.post(
            QA_API_URL.replace('/api/v1/chat/completions', '/v1/chat/completions'),  # Fix endpoint
            headers={"Content-Type": "application/json"},
            json={
                "model": QA_MODEL,
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 4000,
                "top_p": 0.8,
                "stream": False
            }
        )
        response.raise_for_status()
        
        # Add error checking for the response
        response_data = response.json()
        if 'error' in response_data:
            raise Exception(response_data['error'])
            
        return response_data['choices'][0]['message']['content']
        
    except Exception as e:
        print(f"Error getting LLM response: {e}")
        return f"Error: Could not generate response. {str(e)}"

def get_answer(question: str) -> Answer:
    try:
        # Search for relevant content
        results = search_similar_content(question)        
        if results:
            # Get LLM response
            response = get_llm_response(question, results)
            return Answer(text=response, confidence=0.9)
        else:
            return Answer(
                text="I couldn't find any relevant information to answer your question. Could you try rephrasing it?",
                confidence=0.1
            )
            
    except Exception as e:
        print(f"Error in QA system: {e}")
        import random
        # Return a fallback response
        return Answer(
            text=random.choice(fallback_responses),
            confidence=0.1
        )
 