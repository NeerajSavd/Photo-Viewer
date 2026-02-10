# Image Tagging Application

A photo library application with advanced search capabilities using AI-powered image tagging.

## Features

- **AI-Powered Tagging**: Automatically extracts and tags images using LLM
- **Multi-Criteria Search**: Search by date range, location, and tags
- **On This Day View**: See photos from the same day in the past
- **Modern UI**: Beautiful interface for browsing and managing your photo library

## Tech Stack

- **Backend**: Python with SQLite database
- **AI Integration**: LLM for intelligent image tagging
- **Frontend Options**:
  - **Flet**: Desktop application (src/photos.py)
  - **Streamlit**: Web-based application (src/photos_streamlit.py)

## Installation

### Prerequisites

- Python 3.8+
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

### Using Flet (Desktop App)

```bash
python src/photos.py
```

### Using Streamlit (Web App)

```bash
streamlit run src/photos_streamlit.py
```

Then open your browser to `http://localhost:8501`

## Project Structure

```
src/
├── photos.py              # Flet desktop application
├── photos_streamlit.py    # Streamlit web application
├── gui_elements.py        # UI components (Flet)
├── search.py              # Search functionality
├── image_tagging.py       # Image analysis and tagging
├── analysis.py            # Image metadata extraction
└── database.py            # Database operations

Test Data/                 # Sample images for testing
output/                    # Generated files
```

## TODO

- Map view
- Click to see full-size image with metadata overlay
- Visual tag frequency display
- Recent photos
- Date range picker
- Location radius
- Tag combinations (AND/OR/NOT)
- Smart suggestions
- Fuzzy search/semantic search
- Edit tags manually
- Remove tags from deleted images
- Smart albums
- Folder management
- Image sorting
- Face detection
