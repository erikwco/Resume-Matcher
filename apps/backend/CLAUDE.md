# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the backend component of Resume Matcher, an AI-powered platform that helps users optimize their resumes for ATS compatibility. The backend is a FastAPI application with AI agent capabilities for resume analysis and job matching.

## Development Commands

### Setup and Installation
```bash
# Install backend dependencies (from project root)
uv venv && uv pip install .

# Install all dependencies (frontend + backend, from project root)
npm run install
```

### Development Server
```bash
# Start backend only
uv run uvicorn app.main:app --reload --port 8000 --timeout-keep-alive 300 --timeout-graceful-shutdown 300

# Start both frontend and backend (from project root)
npm run dev
```

### Building and Production
```bash
# Build backend
uv run python -c "print('Backend build complete')"

# Build entire project (from project root)
npm run build
```

### Testing and Linting
```bash
# No specific test commands configured yet
# Linting is handled at the frontend level only
```

## Architecture Overview

### Core Structure
- **FastAPI Application**: Main app created in `app/base.py` with lifespan management for database initialization
- **Agent System**: Multi-provider AI agent architecture supporting OpenAI, Gemini, and Ollama models
- **Database**: SQLite/SQLAlchemy with async support for resume and job data storage
- **API Routes**: RESTful endpoints under `/api/v1/` for resume and job operations

### Key Components

#### Agent Manager (`app/agent/manager.py`)
- **AgentManager**: Orchestrates AI providers (OpenAI, Gemini, Ollama) with fallback strategy
- **EmbeddingManager**: Handles text embeddings for similarity analysis
- Provider selection based on available API keys, falls back to Ollama if local models available
- Supports JSON and Markdown output strategies

#### Database Models (`app/models/`)
- **Resume**: Stores resume data with metadata and processing status
- **Job**: Stores job descriptions and requirements
- **User**: Basic user management
- **Association**: Links between resumes and jobs for matching

#### Services (`app/services/`)
- **ResumeService**: Resume processing, parsing, and analysis
- **JobService**: Job description processing and keyword extraction
- **ScoreImprovementService**: AI-powered resume improvement suggestions

#### API Routes (`app/api/router/v1/`)
- **Resume endpoints**: Upload, process, analyze resumes
- **Job endpoints**: Process job descriptions, match with resumes

### Configuration (`app/core/config.py`)
- Environment-based settings with Pydantic
- Database URL configuration for sync/async operations
- CORS origins for frontend integration
- Session and security settings

### AI Provider Integration
The system supports three AI providers with automatic fallback:
1. **OpenAI**: Requires `OPENAI_API_KEY` environment variable
2. **Gemini**: Requires `GEMINI_API_KEY` environment variable  
3. **Ollama**: Local models, requires installed models (default: `gemma3:4b`)

For Ollama, check available models with: `ollama list`
Install models with: `ollama pull <model-name>`

### Database Schema
- Uses SQLAlchemy async engine with automatic table creation on startup
- Models inherit from `Base` class with common fields (id, created_at, updated_at)
- Supports both SQLite (development) and PostgreSQL (production) via `ASYNC_DATABASE_URL`

### Environment Variables
Required environment variables (create `.env` file in project root):
```bash
SESSION_SECRET_KEY=your-secret-key
ASYNC_DATABASE_URL=sqlite+aiosqlite:///./resume_matcher.db  # or PostgreSQL URL
SYNC_DATABASE_URL=sqlite:///./resume_matcher.db  # for sync operations
OPENAI_API_KEY=your-openai-key  # optional
GEMINI_API_KEY=your-gemini-key  # optional
```

### Development Workflow
1. Ensure Ollama is installed and running for local AI models
2. Install dependencies with `uv` package manager
3. Run development server with auto-reload enabled
4. API documentation available at `http://localhost:8000/api/docs`
5. Frontend integration expects backend on port 8000

### File Processing
The application processes PDF resumes and text job descriptions using:
- PDF parsing with `pdfminer.six`
- Text extraction and cleaning
- Structured data extraction using AI providers
- Similarity scoring between resumes and job requirements