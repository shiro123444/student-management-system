# Educational QA Bot

An AI-powered educational question-answering system built with modern web technologies and advanced retrieval-augmented generation (RAG) capabilities.

## 🎯 Overview

This educational QA bot provides intelligent answers to educational questions using a combination of:
- **FastAPI backend** with RAG pipeline
- **Vue 3 frontend** with accessibility features
- **Knowledge graph** storage (Neo4j)
- **Vector search** capabilities (Milvus)
- **Docker-based** infrastructure

## 🚀 Features

### For Students & Educators
- **Intelligent Q&A**: Ask questions on any educational topic
- **Source Citations**: Get references for all answers
- **Follow-up Suggestions**: Discover related topics
- **Conversation History**: Track your learning journey

### Accessibility Features
- **High Contrast Mode**: Enhanced visibility
- **Text-to-Speech**: Audio reading of responses
- **Large Text Support**: Improved readability
- **Keyboard Navigation**: Full keyboard accessibility
- **Screen Reader Support**: ARIA labels and announcements

### For Administrators
- **Content Ingestion**: Upload educational materials
- **Analytics Dashboard**: Track usage and performance
- **Export Reports**: Generate usage and knowledge gap reports
- **Knowledge Graph Visualization**: Explore content relationships

## 🏗️ Architecture

### Backend Components
- **FastAPI** application with async support
- **RAG Pipeline** with retrieval, reranking, and context management
- **Neo4j** for knowledge graph storage
- **Milvus** for vector similarity search
- **Redis** for caching and session management

### Frontend Components
- **Vue 3** with TypeScript and Composition API
- **Vite** for fast development and building
- **Accessible UI** with WCAG 2.1 AA compliance
- **Responsive Design** for all devices

## 🛠️ Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/shiro123444/student-management-system.git
   cd student-management-system
   ```

2. **Start the application**
   ```bash
   cd infra/docker
   docker-compose up -d
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Neo4j Browser: http://localhost:7474
   - MinIO Console: http://localhost:9001

### Local Development

#### Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Run development server
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
# Install dependencies
cd frontend
npm install

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Run development server
npm run dev
```

## 📚 API Documentation

### Core Endpoints

#### Health Check
```http
GET /api/health
```

#### Chat
```http
POST /api/chat
Content-Type: application/json

{
  "query": "What is machine learning?",
  "session_id": "optional-session-id",
  "include_sources": true,
  "max_sources": 3
}
```

#### File Ingestion
```http
POST /api/ingest/file
Content-Type: multipart/form-data

file: <file>
document_type: "educational_content"
metadata: "{\"subject\": \"computer_science\"}"
```

#### Export Reports
```http
POST /api/export/report?report_type=usage&format=json
```

For detailed API documentation, visit http://localhost:8000/docs when running the application.

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Tests
```bash
cd frontend
npm run test
npm run type-check
npm run lint
```

### Integration Tests
```bash
cd infra/docker
docker-compose up -d
# Run integration test scripts
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
# API Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Database Configuration
NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

MILVUS_HOST=localhost
MILVUS_PORT=19530

# External APIs
OPENAI_API_KEY=your-openai-api-key
```

#### Frontend (.env)
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE="Educational QA Bot"
VITE_ENABLE_TTS=true
```

## 📊 Monitoring & Analytics

### Health Monitoring
- Application health: `/api/health`
- System metrics: CPU, memory, disk usage
- Database connectivity checks

### Usage Analytics
- Query patterns and frequency
- Response quality metrics
- User interaction tracking
- Knowledge gap identification

## 🚀 Deployment

### Production Deployment

1. **Build and push Docker images**
   ```bash
   docker build -t educational-qa-backend -f backend/Dockerfile .
   docker build -t educational-qa-frontend -f frontend/Dockerfile ./frontend
   ```

2. **Deploy with Docker Compose**
   ```bash
   cd infra/docker
   docker-compose -f docker-compose.yml up -d
   ```

3. **Set up reverse proxy** (Nginx/Traefik)
4. **Configure SSL certificates**
5. **Set up monitoring** (Prometheus/Grafana)

### Scaling Considerations
- **Horizontal scaling**: Multiple API instances behind load balancer
- **Database scaling**: Neo4j clustering, Milvus sharding
- **CDN integration**: Static asset distribution
- **Caching layers**: Redis clustering

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

### Code Standards
- **Python**: Black formatting, flake8 linting, mypy type checking
- **TypeScript**: ESLint, Prettier formatting
- **Commits**: Conventional commit messages
- **Documentation**: Update relevant docs

### Running Quality Checks
```bash
# Backend
black backend/app --check
flake8 backend/app
mypy backend/app
pytest backend/tests/

# Frontend
npm run lint
npm run type-check
npm run build
```

## 📝 Documentation

- **API Documentation**: Available at `/docs` endpoint
- **Architecture Guide**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Knowledge Graph Design**: [docs/KNOWLEDGE_GRAPH_DESIGN.md](docs/KNOWLEDGE_GRAPH_DESIGN.md)
- **Deployment Guide**: Coming soon

## 🛡️ Security

### Security Features
- **Input sanitization**: XSS prevention
- **Rate limiting**: API abuse prevention
- **CORS configuration**: Cross-origin protection
- **Content Security Policy**: Script injection prevention

### Data Privacy
- **Query anonymization**: PII removal from logs
- **Session isolation**: User data separation
- **Secure storage**: Encrypted sensitive data

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI**: Modern Python web framework
- **Vue.js**: Progressive JavaScript framework
- **Neo4j**: Graph database platform
- **Milvus**: Vector similarity search engine
- **OpenAI**: Language model capabilities

## 📞 Support

For questions and support:
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Documentation**: In-app help and guides

---

**Educational QA Bot** - Empowering learning through intelligent question answering 🎓
