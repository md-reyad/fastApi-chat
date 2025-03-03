# FastAPI Web Application

A robust web application built with FastAPI that provides data processing capabilities, database integration, and a question-answering system.

## Features

- RESTful API built with FastAPI
- Data validation using Pydantic
- Data processing with NumPy
- Database integration with SQLAlchemy and PostgreSQL
- Natural Language Processing capabilities with scikit-learn
- Interactive API documentation
- Rich console formatting for QA system

## Requirements

- Python 3.8+
- PostgreSQL (if using database features)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory with the following variables:
   ```
   DATABASE_URL=postgresql://username:password@localhost/dbname
   # Add other environment variables as needed
   ```

## Usage

Start the server:
```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

API documentation is automatically generated and available at:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

## Project Structure

```
project/
├── main.py              # FastAPI application entry point
├── qa_system.py         # Question-answering system implementation
├── requirements.txt     # Project dependencies
├── .env                 # Environment variables (not in version control)
└── README.md            # Project documentation
```

## API Endpoints

### GET /api/chat
Retrieves chat history or specific chat messages.

Query Parameters:
- `limit`: Maximum number of messages to return (default: 50)
- `offset`: Number of messages to skip (for pagination)

Response:
```json
{
  "messages": [
    {
      "id": "msg_123",
      "content": "Hello, what is fundednext?",
      "role": "system",
      "timestamp": "2023-11-15T14:30:45Z"
    },
    {
      "id": "msg_124",
      "content": "I have a question about fundednext",
      "role": "system",
      "timestamp": "2023-11-15T14:31:12Z"
    }
  ],
  "total": 120
}
```

### POST /api/chat
Sends a message to the QA system and returns the response.

Request Body:
```json
{
  "message": "What is fundednext?",
  "context": {
    "conversation_id": "conv_789",
    "metadata": {
      "source": "web",
      "user_id": "user_456"
    }
  }
}
```

Response:
```json
{
  "id": "msg_125",
  "content": "FastAPI is a modern, fast web framework for building APIs with Python 3.7+ based on standard Python type hints. It's designed to be easy to use and high performance.",
  "role": "assistant",
  "timestamp": "2023-11-15T14:32:05Z",
  "metadata": {
    "confidence": 0.95,
    "sources": ["fastapi_docs", "python_libraries"]
  }
}
```


## QA System

The application includes a question-answering system implemented in `qa_system.py`. This system uses scikit-learn for basic NLP processing and provides formatted console output using the Rich library.

To use the QA system directly:

```python
from qa_system import QASystem

qa = QASystem()
answer = qa.get_answer("What is fundednext?")
print(answer)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

[MIT License](https://opensource.org/licenses/MIT)