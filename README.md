 One Piece RAG PROJECT

## About
This project builds a One Piece RAG (Retrieval-Augmented Generation) Bot that can answer questions about the One Piece universe and return relevant URLs/references from the wiki data. The bot uses embeddings and vector search to find relevant information, then uses OpenAI's API to generate comprehensive answers.

## Status: 🚧 Work in Progress

### Current Progress
- ✅ Project setup and requirements
- 🔄 **Currently working on**: Parsing One Piece chapters
- 📊 **Latest chapter processed**: Chapter 1156

### Folder Structure (Target)
```
one_piece_rag/
├── data/
│   ├── raw/              # Raw scraped data
│   └── processed/        # Cleaned and processed data
├── src/
│   ├── scraper/          # Web scraping modules
│   ├── embeddings/       # Text embedding generation
│   ├── database/         # Vector database management
│   ├── retrieval/        # Search and retrieval logic
│   └── app/              # Streamlit application
├── requirements.txt
└── README.md
```

## To Do Next

### Data Collection & Parsing
- [ ] Complete chapter parsing for all available chapters
- [ ] Parse character information and profiles
- [ ] Parse story arcs and their details
- [ ] Parse anime episode information
- [ ] Parse locations, Devil Fruits, and other One Piece entities

### RAG Pipeline Development
- [ ] Implement text chunking and preprocessing
- [ ] Generate embeddings for processed text
- [ ] Set up vector database (ChromaDB/FAISS)
- [ ] Build retrieval system with similarity search
- [ ] Integrate OpenAI API for answer generation
- [ ] Create Streamlit web interface
- [ ] Add reference URL tracking and display
- [ ] Testing and optimization


## Tech Stack
- **Scraping**: BeautifulSoup, Requests
- **Embeddings**: OpenAI, Sentence Transformers
- **Vector DB**: ChromaDB, FAISS
- **LLM**: OpenAI GPT
- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy