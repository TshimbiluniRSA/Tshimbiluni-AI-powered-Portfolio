# Tshimbiluni-AI-powered-Portfolio

> A modern, AI-powered portfolio website with intelligent chat assistant, GitHub/LinkedIn integration, and responsive design.

## 🌟 Features

- **AI-Powered Chat**: Integrated chat interface supporting multiple LLM providers (LLaMA, OpenAI, Anthropic, Gemini, Ollama)
- **GitHub Integration**: Automatic sync and display of GitHub profile data
- **LinkedIn Integration**: Scrape and display LinkedIn profile information
- **Responsive Design**: Mobile-first, fully responsive UI
- **Modern Tech Stack**: React + TypeScript frontend, FastAPI backend
- **Containerized**: Full Docker support for easy deployment
- **RESTful API**: Well-documented API with OpenAPI/Swagger docs

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose (recommended)
- OR Node.js 20+ and Python 3.11+ for local development

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/TshimbiluniRSA/Tshimbiluni-AI-powered-Portfolio.git
   cd Tshimbiluni-AI-powered-Portfolio
   ```

2. **Set up environment variables**
   ```bash
   # Backend
   cp backend/.env.example backend/.env
   # Edit backend/.env with your API keys and configuration
   # See SECRETS_SETUP.md for detailed instructions on obtaining and configuring API keys
   
   # Frontend
   cp frontend/.env.example frontend/.env.local
   # Edit frontend/.env.local with your configuration
   ```

3. **Start the application**
   ```bash
   # Production mode
   docker-compose up -d
   
   # Development mode (with hot reload)
   docker-compose -f docker-compose.dev.yml up
   ```

4. **Access the application**
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Local Development (Without Docker)

#### Backend Setup

```bash
cd backend
pip install -r src/requirements.txt
cp .env.example .env
# Edit .env with your configuration

# Run the backend
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local with your configuration

# Run the frontend
npm run dev
```

## 📁 Project Structure

```
Tshimbiluni-AI-powered-Portfolio/
├── backend/                 # FastAPI backend
│   ├── src/
│   │   ├── main.py         # Application entry point
│   │   ├── routers/        # API route handlers
│   │   ├── services/       # Business logic
│   │   ├── db/             # Database models and config
│   │   ├── schemas.py      # Pydantic schemas
│   │   └── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/               # React + TypeScript frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── api/           # API client
│   │   ├── App.tsx        # Main app component
│   │   └── main.tsx       # Entry point
│   ├── Dockerfile
│   ├── nginx.conf         # Nginx configuration
│   └── .env.example
│
├── docker-compose.yml      # Production compose file
└── docker-compose.dev.yml  # Development compose file
```

## ⚙️ Configuration

### Backend Environment Variables

Key environment variables for the backend (see `backend/.env.example` for full list):

```env
# LLM Provider (choose one)
LLAMA_API_URL=https://api-inference.huggingface.co/models/...
HUGGINGFACE_TOKEN=your_token_here
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
OLLAMA_BASE_URL=http://localhost:11434

# GitHub
GITHUB_TOKEN=your_github_token

# Database
DATABASE_URL=sqlite+aiosqlite:///./portfolio.db
```

**📚 For detailed instructions on obtaining and configuring API keys, see [SECRETS_SETUP.md](SECRETS_SETUP.md)**

### Frontend Environment Variables

```env
VITE_API_URL=http://localhost:8000
VITE_GITHUB_USERNAME=your_username
```

## 🔌 API Endpoints

### Chat Endpoints
- `POST /chat/message` - Send a message to AI
- `POST /chat/stream` - Stream AI responses
- `GET /chat/sessions/{session_id}` - Get chat session
- `GET /chat/sessions` - List all sessions
- `DELETE /chat/sessions/{session_id}` - Delete session

### GitHub Endpoints
- `POST /github/sync` - Sync GitHub profile
- `GET /github/profiles/{username}` - Get GitHub profile
- `GET /github/profiles` - List profiles

### LinkedIn Endpoints
- `POST /linkedin/sync` - Sync LinkedIn profile
- `GET /linkedin/profiles/{url}` - Get LinkedIn profile

Full API documentation available at `/docs` when running the backend.

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Build Tests
```bash
# Test backend Docker build
docker build -t portfolio-backend ./backend

# Test frontend build
cd frontend && npm run build
```

## 🚢 Deployment

### Docker Deployment

1. Build and push images:
   ```bash
   docker-compose build
   docker-compose push  # If using a registry
   ```

2. Deploy on server:
   ```bash
   docker-compose up -d
   ```

### Environment-Specific Deployment

For production, ensure you:
- Use production-grade database (PostgreSQL recommended)
- Set secure SECRET_KEY
- Configure proper CORS origins
- Use HTTPS/SSL certificates
- Set up monitoring and logging
- Configure rate limiting

## 🛠️ Technology Stack

### Frontend
- React 19
- TypeScript
- Vite
- Axios
- CSS3

### Backend
- Python 3.11
- FastAPI
- SQLAlchemy (async)
- Multiple LLM providers support
- Pydantic for validation

### Infrastructure
- Docker & Docker Compose
- Nginx (for frontend)
- SQLite (development) / PostgreSQL (production)

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Tshimbiluni**
- GitHub: [@TshimbiluniRSA](https://github.com/TshimbiluniRSA)

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## ⭐ Show your support

Give a ⭐️ if this project helped you!