# Image Tagging Application

A photo library application with advanced search capabilities using AI-powered image tagging.

## Features

- **AI-Powered Tagging**: Automatically extracts and tags images using LLM
- **Multi-Criteria Search**: Search by date range, location, and tags
- **On This Day View**: See photos from the same day in the past
- **Modern UI**: Beautiful interface for browsing and managing your photo library
- **Search Operators**: AND/OR/NOT search operators
- **Image Details**: See photo metadata and assigned tags

## Tech Stack

- **Backend**: Python with SQLite database
- **AI Integration**: LLM for intelligent image tagging
- **Frontend**: Vue.js for web-based application

## Installation

### Prerequisites

- Python 3.13
- Required packages (see requirements.txt)

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env`:
```
SEARCH_MODEL_URL=your_llm_api_url
DB_PATH=path/to/your/database.db
```

3. Add image folders to `folders.txt`

## Running the Application

1. Run the backend:
```bash
cd src && python app.py
```

2. Run the frontend:
```bash
cd frontend && npm run dev
```

## TODO
- Map view
- Visual tag frequency display
- Recent photos
- Location radius
- Smart suggestions
- Fuzzy search/semantic search
- Edit tags manually
- Remove tags from deleted images
- Smart albums
- Folder management
- Image sorting
- Face detection