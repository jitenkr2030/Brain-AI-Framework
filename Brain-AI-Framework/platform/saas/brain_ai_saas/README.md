# 🧠 Brain AI SaaS Platform

A production-ready SaaS platform built on the Brain AI Framework, featuring persistent memory, continuous learning, and enterprise-grade architecture.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- At least 4GB RAM available
- Ports 80, 3000, 3001, 5432, 6379, 8000, 8080, 9090, 1025, 8025 available

### One-Command Launch
```bash
# Make script executable (if needed)
chmod +x start-saas.sh

# Start the entire platform
./start-saas.sh
```

### Manual Setup
```bash
# 1. Copy environment template
cp .env.example .env

# 2. Update .env with your configuration
nano .env

# 3. Start services
docker-compose up -d

# 4. Check status
docker-compose ps
```

## 🌐 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend Dashboard** | http://localhost:3000 | React-based admin interface |
| **Backend API** | http://localhost:8000 | FastAPI REST API |
| **API Documentation** | http://localhost:8000/docs | Interactive API docs |
| **Database Admin** | http://localhost:8080 | Adminer database interface |
| **Monitoring** | http://localhost:3001 | Grafana dashboards |
| **Metrics** | http://localhost:9090 | Prometheus metrics |
| **Email Testing** | http://localhost:8025 | MailHog email interface |

## 📋 Default Credentials

| Service | Username | Password |
|---------|----------|----------|
| Database | postgres | brain_ai_password_2025 |
| Grafana | admin | brain_ai_grafana_2025 |
| Adminer | postgres | brain_ai_password_2025 |
| Redis | (password required) | brain_ai_redis_2025 |

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Load Balancer (Nginx)                    │
├─────────────────────────────────────────────────────────────┤
│  Frontend Dashboard │ Admin Portal │ API Gateway           │
├─────────────────────────────────────────────────────────────┤
│                    Brain AI Backend                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Auth Service│ │ Memory      │ │ Learning    │          │
│  │             │ │ Service     │ │ Service     │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Analytics   │ │ Billing     │ │ Project     │          │
│  │ Service     │ │ Service     │ │ Service     │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│                     Data Layer                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ PostgreSQL  │ │ Redis Cache │ │ Vector DB   │          │
│  │ (Main DB)   │ │ (Sessions)  │ │ (Pinecone)  │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Key Features

### 🧠 Brain AI Core
- **Persistent Memory**: Never loses learned patterns
- **Continuous Learning**: Improves with every interaction
- **Multi-type Memories**: Episodic, semantic, procedural, working, associative
- **Vector Search**: Semantic similarity matching
- **Strength-based Activation**: Brain-like memory retrieval

### 🏢 Multi-Tenant SaaS
- **Tenant Isolation**: Complete data separation
- **Role-based Access**: Admin, user, viewer permissions
- **API Rate Limiting**: Per-tenant quotas and limits
- **Subscription Management**: Plan-based feature access
- **Usage Tracking**: Comprehensive analytics

### 📊 Enterprise Features
- **Real-time Analytics**: Performance and usage metrics
- **Health Monitoring**: System status and alerts
- **Export/Import**: Data portability and backup
- **Security**: JWT authentication, CORS, rate limiting
- **Scalability**: Docker containerization, load balancing

### 🎛️ Management Dashboard
- **Project Management**: Organize memories by use case
- **Memory Visualization**: Interactive memory browser
- **Learning Analytics**: Track improvement over time
- **User Management**: Tenant and user administration
- **System Health**: Real-time monitoring dashboard

## 🛠️ Development

### Project Structure
```
brain_ai_saas/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── main.py         # Main application
│   │   ├── config.py       # Configuration
│   │   ├── database.py     # Database connection
│   │   ├── models/         # Pydantic models
│   │   ├── routers/        # API endpoints
│   │   ├── services/       # Business logic
│   │   └── dependencies.py # Auth & middleware
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile         # Container config
├── frontend/               # React application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── api/           # API clients
│   │   └── contexts/      # React contexts
│   └── Dockerfile.dev     # Development container
├── deployment/             # Deployment configs
│   └── nginx/             # Nginx configuration
├── monitoring/             # Observability
│   ├── prometheus/        # Metrics config
│   └── grafana/           # Dashboard configs
├── docker-compose.yml     # Service orchestration
├── start-saas.sh          # Startup script
└── README.md              # This file
```

### API Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User authentication
- `POST /api/v1/auth/logout` - Session termination
- `GET /api/v1/auth/me` - Current user profile
- `PUT /api/v1/auth/me` - Update profile

#### Tenants
- `POST /api/v1/tenants/` - Create tenant (admin)
- `GET /api/v1/tenants/` - List tenants (admin)
- `GET /api/v1/tenants/me` - Current tenant info
- `PUT /api/v1/tenants/me` - Update tenant

#### Projects
- `POST /api/v1/projects/` - Create project
- `GET /api/v1/projects/` - List projects
- `GET /api/v1/projects/{id}` - Get project
- `PUT /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

#### Memories
- `POST /api/v1/memories/` - Create memory
- `GET /api/v1/memories/project/{id}` - List project memories
- `POST /api/v1/memories/search` - Search memories
- `GET /api/v1/memories/{id}` - Get memory
- `PUT /api/v1/memories/{id}` - Update memory
- `DELETE /api/v1/memories/{id}` - Delete memory

#### Learning
- `POST /api/v1/learning/feedback` - Submit feedback
- `GET /api/v1/learning/analytics/{id}` - Learning analytics
- `GET /api/v1/learning/insights/{id}` - AI insights
- `GET /api/v1/learning/health` - System health

### Database Schema

#### Core Tables
- **tenants**: Multi-tenant organization
- **users**: User accounts and authentication
- **projects**: Memory organization containers
- **memories**: Brain AI persistent memories
- **learning_events**: Feedback and learning data
- **api_usage**: Rate limiting and analytics
- **subscriptions**: Billing and plan management

## 🚀 Deployment

### Production Checklist
- [ ] Update `.env` with production values
- [ ] Change all default passwords
- [ ] Set up SSL certificates
- [ ] Configure monitoring alerts
- [ ] Set up backup strategy
- [ ] Enable vector database (Pinecone)
- [ ] Configure email service
- [ ] Set up domain and DNS

### Environment Variables
```bash
# Required for production
SECRET_KEY=your_super_secret_key
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://:password@host:6379/0
PINECONE_API_KEY=your_pinecone_key

# Optional integrations
OPENAI_API_KEY=your_openai_key
SENTRY_DSN=your_sentry_dsn
SMTP_HOST=your_smtp_host
```

### Docker Production
```bash
# Build production images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 📈 Monitoring & Analytics

### Prometheus Metrics
- HTTP request duration and count
- Memory operation statistics
- Database connection pool usage
- Redis cache hit rates
- Learning system performance

### Grafana Dashboards
- **System Overview**: Key metrics and health
- **API Performance**: Response times and throughput
- **Learning Analytics**: Feedback and improvement trends
- **Resource Usage**: CPU, memory, and storage

### Health Checks
- `/health` - Basic health status
- `/health/detailed` - Comprehensive system check
- `/metrics` - Prometheus metrics endpoint

## 🔒 Security

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (RBAC)
- API key authentication for tenants
- Session management with Redis

### Data Protection
- Tenant data isolation
- Encrypted password storage (bcrypt)
- SQL injection prevention
- XSS protection headers
- CORS configuration

### Rate Limiting
- Per-IP rate limiting
- Per-tenant quotas
- Burst protection
- Configurable limits by plan

## 🧪 Testing

### Run Tests
```bash
# Backend tests
cd backend
python -m pytest tests/ -v

# Frontend tests
cd frontend
npm test

# Load testing
cd deployment
k6 run load-test.js
```

### Test Data
```bash
# Create test tenant and user
curl -X POST http://localhost:8000/api/v1/tenants/ \
  -H "Authorization: Bearer admin-token" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Corp","slug":"test","plan":"professional"}'
```

## 🆘 Troubleshooting

### Common Issues

#### Services not starting
```bash
# Check logs
docker-compose logs -f

# Restart specific service
docker-compose restart backend

# Reset everything
docker-compose down -v
docker-compose up -d
```

#### Database connection issues
```bash
# Check PostgreSQL
docker-compose exec postgres psql -U postgres -d brain_ai_saas

# Reset database
docker-compose down -v
docker-compose up -d
```

#### Memory issues
```bash
# Check resource usage
docker stats

# Increase memory limits in docker-compose.yml
```

### Logs Location
- **Backend**: `docker-compose logs -f backend`
- **Database**: `docker-compose logs -f postgres`
- **Redis**: `docker-compose logs -f redis`
- **Frontend**: `docker-compose logs -f frontend`

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone <repository-url>
cd brain_ai_saas

# Start development environment
./start-saas.sh

# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

### Code Standards
- **Python**: Black formatting, isort imports, mypy type checking
- **TypeScript**: ESLint, Prettier formatting
- **Git**: Conventional commits, signed commits preferred

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: [docs/](./docs/)
- **API Docs**: http://localhost:8000/docs
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

---

**Brain AI SaaS Platform v1.0.0** - Transforming AI with persistent memory and continuous learning 🧠✨
