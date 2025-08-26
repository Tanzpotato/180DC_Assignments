# AI Legal Debate

## Project Structure 

Challenge-3/
│
├── backend/app/
│   ├── main.py          # FastAPI backend (debate orchestration & API endpoints)
│   ├── retrieval.py     # Loads and parses legal case corpus
│   ├── generator.py     # Selects and generates cases from corpus
│   ├── models.py        # Wrappers connecting LLM logic and app
│   ├── llm.py           # RAG lawyer, chaos lawyer, judge, embeddings
│   ├── config.py        # Configuration settings
│   └── __init__.py      # Package initializer
│
├── frontend/
│   └── streamlit_app.py # Streamlit UI for interactive debate
│
├── Metadata/
│   └── cases.jsonl      # Dataset of legal cases with metadata
│
├── utils/
│   └── generate_facts.py # Expands cases into structured factual snippets
│
├── requirements.txt     # Project dependencies
└── README.md            # Project documentation

# Prerequisites

> Core backend
fastapi==0.110.0
uvicorn==0.27.1

> Frontend
streamlit==1.32.0
requests==2.31.0

> Retrieval & Embeddings
sentence-transformers==2.2.2
torch>=1.10.0
scikit-learn==1.4.1.post1
numpy==1.26.4
scipy==1.12.0

> Utilities
python-dotenv==1.0.1  

