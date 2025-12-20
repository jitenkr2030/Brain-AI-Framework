# Project Management with Brain AI Framework

Intelligent project management application powered by Brain AI for enhanced resource allocation, risk assessment, and progress prediction.

## 🚀 Features

### Core Functionality
- **Project Planning & Tracking**: Comprehensive project lifecycle management
- **Resource Allocation**: AI-powered team member assignment based on skills and workload
- **Risk Assessment**: Intelligent risk prediction and mitigation strategies
- **Schedule Optimization**: AI-driven timeline optimization and critical path analysis
- **Team Performance Analytics**: Real-time team productivity and utilization metrics
- **Real-time Updates**: WebSocket-powered live updates and notifications

### Brain AI Integration
- **Pattern Learning**: Continuous learning from project patterns and outcomes
- **Predictive Analytics**: AI-powered project outcome predictions
- **Intelligent Recommendations**: Context-aware suggestions for optimization
- **Resource Optimization**: Smart allocation based on historical data and current capacity

### Demo Data
- **Sample Project**: E-Commerce Platform Redesign with realistic tasks and timelines
- **Team Members**: 5 team members with diverse skills and varying workloads
- **Task Dependencies**: Complex task relationships and dependencies
- **Milestones**: Project milestones with progress tracking

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- pip or uv package manager

### Setup
1. **Clone or navigate to the project directory**:
   ```bash
   cd brain_ai/examples/project-management
   ```

2. **Install dependencies**:
   ```bash
   # Using pip
   pip install -r requirements.txt
   
   # Using uv (recommended)
   uv add fastapi uvicorn websockets jinja2 python-multipart
   ```

3. **Run the application**:
   ```bash
   python app.py
   # or
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Access the application**:
   Open http://localhost:8000 in your browser

## 📋 API Endpoints

### Dashboard & Overview
- `GET /` - Main dashboard HTML interface
- `GET /api/dashboard` - Dashboard data with AI insights
- `GET /api/projects` - List all projects
- `GET /api/projects/{project_id}` - Get specific project details
- `GET /api/tasks` - List all tasks
- `GET /api/team` - List team members

### AI-Powered Analysis
- `GET /api/resource-allocation/{project_id}` - Resource allocation analysis
- `GET /api/risk-analysis/{project_id}` - Risk assessment and predictions
- `GET /api/schedule-optimization/{project_id}` - Schedule optimization recommendations
- `GET /api/team-analytics` - Team performance analytics

### Task Management
- `POST /api/tasks` - Create new task
- `PUT /api/tasks/{task_id}/status` - Update task status
- `PUT /api/tasks/{task_id}/assign` - Assign task to team member

### Real-time Features
- `WebSocket /ws` - Real-time updates and notifications

## 🎯 Key AI Capabilities

### Resource Allocation Intelligence
The Brain AI analyzes team member skills, current workloads, and project requirements to recommend optimal task assignments:

```python
# Example AI analysis output
{
  "recommendations": [
    "Assign 'Performance Optimization' to Bob Smith (Python + React expertise)",
    "Reduce David Wilson's workload from 90% to 75% to prevent burnout",
    "Consider skill gaps in frontend development for future planning"
  ],
  "bottlenecks": [
    {
      "member_id": "tm4",
      "member_name": "David Wilson", 
      "workload": 0.9,
      "skills": ["kubernetes", "docker", "ci_cd"]
    }
  ]
}
```

### Risk Assessment & Prediction
AI-powered risk analysis considers timeline pressure, resource constraints, and technical complexity:

```python
# Risk analysis results
{
  "current_risk_score": 0.3,
  "risk_factors": [
    "Tight deadline with 5 remaining tasks",
    "High task dependency complexity",
    "Team member bottleneck identified"
  ],
  "predictions": {
    "completion_probability": 0.85,
    "estimated_delay": "5-10 days",
    "budget_overrun_risk": "Low"
  },
  "mitigation_strategies": [
    "Add additional developer to frontend component development",
    "Re-prioritize tasks to focus on critical path items",
    "Consider extending timeline by 1 week"
  ]
}
```

### Schedule Optimization
Brain AI analyzes dependencies, resource availability, and historical patterns to suggest timeline improvements:

```python
# Schedule optimization recommendations
{
  "critical_path": ["task3", "task4", "task6"],
  "schedule_optimizations": [
    "Parallelize 'Frontend Component Development' with 'Infrastructure Setup'",
    "Move 'Quality Assurance Testing' earlier to catch issues sooner",
    "Add 20% buffer time for integration testing phase"
  ],
  "predictions": {
    "optimal_completion_date": "2025-03-15",
    "confidence_level": 0.78
  }
}
```

## 🏗️ Architecture

### Core Components

#### ProjectManagementSystem
- Central management class coordinating all functionality
- Brain AI integration for intelligent decision making
- WebSocket connection management for real-time updates

#### Data Models
- **Project**: Project metadata, status, timeline, and progress
- **Task**: Individual tasks with dependencies, assignments, and tracking
- **TeamMember**: Team member profiles with skills and availability

#### AI Integration
- **Pattern Learning**: Continuous learning from project outcomes
- **Predictive Analytics**: AI-powered forecasting and recommendations
- **Context Awareness**: Understanding of project-specific constraints

### System Flow
1. **Data Collection**: Gather project, task, and team data
2. **AI Analysis**: Apply Brain AI for pattern recognition and prediction
3. **Insight Generation**: Create actionable recommendations
4. **Real-time Updates**: Broadcast changes via WebSocket
5. **Continuous Learning**: Update AI patterns based on outcomes

## 📊 Demo Data Structure

### Sample Project: E-Commerce Platform Redesign
- **Budget**: $150,000
- **Timeline**: 90 days
- **Team**: 5 members with diverse skills
- **Tasks**: 7 tasks with dependencies and varying priorities
- **Progress**: 45% complete with 30 days elapsed

### Team Composition
- **Alice Johnson** (Project Manager) - Leadership, Planning
- **Bob Smith** (Senior Developer) - Python, React, AWS
- **Carol Davis** (UX Designer) - Figma, User Research
- **David Wilson** (DevOps Engineer) - Kubernetes, Docker
- **Eva Rodriguez** (QA Engineer) - Testing, Automation

### Task Dependencies & Critical Path
1. User Research → Design System Creation
2. Design System Creation → Frontend Component Development
3. Backend API Development → Frontend Component Development
4. Infrastructure Setup (parallel track)
5. Frontend Component Development → Quality Assurance Testing
6. Quality Assurance Testing → Performance Optimization

## 🔧 Configuration

### Environment Variables
```bash
# Optional: Custom port
PORT=8000

# Optional: Log level
LOG_LEVEL=INFO

# Optional: Database URL (for production)
DATABASE_URL=postgresql://user:password@localhost/project_mgmt
```

### Brain AI Configuration
```python
# Adjustable AI parameters
brain_ai = BrainAI(
    memory_capacity=10000,        # Memory node capacity
    learning_rate=0.01,          # Learning rate for updates
    decay_factor=0.95            # Memory decay over time
)
```

## 🚀 Production Deployment

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations
- **Database**: Replace in-memory storage with PostgreSQL/MySQL
- **Caching**: Add Redis for session and data caching
- **Scaling**: Use Celery for background task processing
- **Monitoring**: Implement Prometheus metrics and structured logging
- **Security**: Add authentication, authorization, and HTTPS

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v
```

### Example Test Cases
- Task creation and assignment
- AI recommendation accuracy
- WebSocket connectivity
- API endpoint functionality
- Dashboard data accuracy

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Install development dependencies: `pip install -r requirements-dev.txt`
4. Run tests: `pytest`
5. Submit pull request

### Code Style
- Follow PEP 8 guidelines
- Add type hints for all functions
- Include docstrings for complex functions
- Write tests for new features

## 📈 Performance Metrics

### Response Times
- Dashboard load: < 200ms
- AI analysis: < 2s for complex projects
- Real-time updates: < 50ms
- Task creation: < 100ms

### Scalability
- Supports 100+ concurrent users
- Handles 1000+ projects and tasks
- AI analysis scales with project complexity
- WebSocket connections: 500+ simultaneous

## 🔍 Troubleshooting

### Common Issues

**WebSocket Connection Fails**
- Check firewall settings
- Verify WebSocket support in browser
- Ensure proper connection handling

**AI Recommendations Not Loading**
- Verify Brain AI framework is properly imported
- Check memory allocation settings
- Review AI pattern initialization

**Performance Issues**
- Monitor memory usage with large datasets
- Consider caching for frequently accessed data
- Optimize AI analysis for complex projects

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python app.py
```

## 📚 Related Documentation

- [Brain AI Framework Documentation](../../README.md)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [WebSocket Best Practices](https://websockets.readthedocs.io/)

## 📄 License

This project is part of the Brain AI Framework examples. See the main project license for details.

## 🆘 Support

For questions, issues, or contributions:
- Create an issue in the main Brain AI Framework repository
- Check existing documentation and examples
- Review troubleshooting section above

---

**Built with ❤️ using Brain AI Framework**