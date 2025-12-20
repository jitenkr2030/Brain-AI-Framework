# 🛠️ Brain AI LMS Setup Guide

## 🚀 Quick Start Guide

This guide will help you set up and run the Brain AI Learning Management System on your local machine.

## 📋 Prerequisites

### System Requirements
- **Node.js**: 18.0.0 or higher
- **Python**: 3.9 or higher
- **PostgreSQL**: 13 or higher
- **Redis**: 6.0 or higher
- **Git**: Latest version

### Accounts Needed
- **Stripe Account**: For payment processing
- **AWS Account**: For file storage and CDN (optional)
- **GitHub Account**: For code management

## 🏗️ Installation Steps

### 1. Clone and Setup Repository

```bash
# Clone the repository
git clone https://github.com/jitenkr2030/Brain-AI-Framework.git
cd Brain-AI-Framework/education/brain_ai_course/lms

# Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup frontend
cd ../frontend
npm install
```

### 2. Database Setup

#### PostgreSQL Configuration
```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb brain_ai_lms

# Create user (optional)
sudo -u postgres psql
CREATE USER brainai WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE brain_ai_lms TO brainai;
\q
```

#### Environment Configuration
Create `.env` files in both backend and frontend directories:

**Backend (.env)**
```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/brain_ai_lms

# JWT Settings
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# AWS Configuration (Optional)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-s3-bucket

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Application Settings
DEBUG=true
API_BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000

# Email Configuration (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

**Frontend (.env.local)**
```env
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_BRAIN_AI_API_URL=http://localhost:8000/api/v1

# Stripe Configuration
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key

# Analytics (Optional)
NEXT_PUBLIC_GA_ID=your_google_analytics_id

# App Configuration
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_APP_NAME=Brain AI LMS
```

### 3. Initialize Database

```bash
# Navigate to backend directory
cd backend

# Run database migrations and seed data
python -c "
from app.database import init_db
init_db()
"

# Or manually:
python -c "
from app.database import create_tables, SeedData
create_tables()
SeedData.create_admin_user()
SeedData.create_sample_courses()
"
```

### 4. Start the Services

#### Start Backend (Terminal 1)
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```

#### Start Redis (Terminal 3) - Optional
```bash
redis-server
```

## 🌐 Access the Application

### Frontend
- **Local Development**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs

### Default Accounts
After running the seed data, you can access:

**Admin Account**
- Email: admin@brainai.com
- Password: admin123

**Test Student Account** (create manually through registration)

## 📁 Project Structure

```
lms/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── main.py            # Application entry point
│   │   ├── database.py        # Database configuration
│   │   ├── models/            # Database models
│   │   ├── routers/           # API endpoints
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   └── utils/             # Utility functions
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables
├── frontend/                  # Next.js Frontend
│   ├── src/
│   │   ├── app/              # App router pages
│   │   ├── components/       # React components
│   │   ├── hooks/            # Custom hooks
│   │   ├── lib/              # Utilities and configurations
│   │   ├── stores/           # State management
│   │   └── types/            # TypeScript types
│   ├── public/               # Static assets
│   ├── package.json          # Node dependencies
│   └── tailwind.config.js    # Tailwind configuration
└── docs/                     # Documentation
```

## 🔧 Configuration Options

### Stripe Setup

1. **Create Stripe Account**: https://stripe.com
2. **Get API Keys**: Dashboard → Developers → API keys
3. **Setup Webhooks**: Dashboard → Developers → Webhooks
   - Endpoint URL: `https://yourdomain.com/api/v1/payments/webhook`
   - Events: `payment_intent.succeeded`, `payment_intent.payment_failed`

### AWS S3 Setup (Optional)

1. **Create S3 Bucket**: AWS Console → S3 → Create bucket
2. **Setup IAM User**: Create user with S3 permissions
3. **Configure CORS**: Allow your domain for file uploads

### Email Configuration (Optional)

For production, configure SMTP settings:
- **Gmail**: Use App Passwords
- **SendGrid**: Use API keys
- **AWS SES**: Configure AWS credentials

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest
```

### Frontend Testing
```bash
cd frontend
npm test
```

### E2E Testing
```bash
cd frontend
npm run test:e2e
```

## 🚀 Production Deployment

### Backend Deployment

#### Docker Setup
```dockerfile
# Dockerfile (backend)
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Environment Variables (Production)
```env
DATABASE_URL=postgresql://user:pass@prod-db:5432/brain_ai_lms
REDIS_URL=redis://prod-redis:6379/0
SECRET_KEY=your-production-secret-key
DEBUG=false
FRONTEND_URL=https://yourdomain.com
```

### Frontend Deployment

#### Vercel Deployment
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel --prod
```

#### Environment Variables (Production)
```env
NEXT_PUBLIC_API_BASE_URL=https://api.yourdomain.com/api/v1
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_key
```

## 📊 Monitoring and Analytics

### Application Monitoring
- **Sentry**: Error tracking
- **LogRocket**: User session replay
- **DataDog**: Performance monitoring

### Analytics
- **Google Analytics**: Web analytics
- **Mixpanel**: User behavior analytics
- **Stripe Dashboard**: Revenue analytics

## 🔐 Security Considerations

### Backend Security
- **Rate Limiting**: Implement API rate limiting
- **Input Validation**: Validate all inputs
- **SQL Injection**: Use ORM and parameterized queries
- **XSS Protection**: Sanitize user inputs

### Frontend Security
- **Content Security Policy**: Configure CSP headers
- **HTTPS Only**: Force HTTPS in production
- **Secure Cookies**: Set secure flags for cookies
- **Dependency Scanning**: Regular security audits

## 🛠️ Development Workflow

### Code Style
- **Backend**: Black formatter, isort, flake8
- **Frontend**: Prettier, ESLint, TypeScript strict mode

### Git Workflow
```bash
# Feature branch workflow
git checkout -b feature/new-feature
git commit -m "Add new feature"
git push origin feature/new-feature
# Create pull request
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Add new feature"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 📞 Support and Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -h localhost -U postgres -d brain_ai_lms
```

**Port Already in Use**
```bash
# Find process using port
lsof -i :8000
kill -9 <PID>
```

**Module Not Found**
```bash
# Reinstall dependencies
pip install -r requirements.txt
npm install
```

### Getting Help
- **Documentation**: Check inline code comments
- **API Documentation**: Visit `/docs` endpoint
- **GitHub Issues**: Report bugs and feature requests

## 🎯 Next Steps

After successful setup:

1. **Customize Branding**: Update colors, logos, and content
2. **Create Content**: Build your first course using the CMS
3. **Test Payments**: Configure Stripe test mode
4. **Setup Analytics**: Add tracking codes
5. **Security Review**: Implement security best practices
6. **Performance Testing**: Load test your application

## 🎉 Success!

You now have a fully functional Brain AI Learning Management System running locally. Start building your world-class AI education platform!

---

*Need help? Check the documentation or create an issue on GitHub.*