# Contributing to GobDatosAgent

Thank you for your interest in contributing to the Investment Data Analysis Agent! 🎉

## 🚀 Quick Start for Contributors

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/YOUR_USERNAME/GobDatosAgent.git`
3. **Create a branch**: `git checkout -b feature/your-feature-name`
4. **Make your changes**
5. **Test thoroughly**
6. **Commit**: `git commit -m "feat: add amazing feature"`
7. **Push**: `git push origin feature/your-feature-name`
8. **Create Pull Request**

## 🛠️ Development Setup

### Prerequisites
- Python 3.8+
- SQL Server access (or Docker for development)
- Git

### Local Development
```bash
# Clone and setup
git clone https://github.com/YOUR_USERNAME/GobDatosAgent.git
cd GobDatosAgent

# Virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Dependencies
pip install -r requirements.txt

# Environment
cp .env.example .env
# Edit .env with your database credentials

# Run tests
python -m pytest tests/
python test_powerbi_integration.py

# Start development server
uvicorn app.main:app --reload
```

## 📋 Contribution Guidelines

### Code Style
- Follow **PEP 8** Python style guide
- Use **type hints** for function parameters and returns
- Add **docstrings** for all functions and classes
- Keep functions **focused and small**

### Commit Messages
Use conventional commits format:
```
feat: add new endpoint for portfolio analysis
fix: resolve SQL Server connection timeout
docs: update PowerBI integration guide
test: add tests for AI analysis service
refactor: optimize database connection pool
```

### Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new functionality
3. **Ensure all tests pass**
4. **Update CHANGELOG.md** if applicable
5. **Reference issue numbers** in PR description

### Testing Requirements

- **Unit tests** for new functions
- **Integration tests** for API endpoints
- **PowerBI integration** tests when applicable
- All tests must **pass** before merge

### Areas for Contribution

#### 🔥 High Priority
- **Performance optimization** of SQL queries
- **Enhanced AI analysis** algorithms
- **PowerBI template** improvements
- **Error handling** and logging
- **Security improvements**

#### 🚀 Features
- **New data sources** integration
- **Additional KPI calculations**
- **Dashboard customization** options
- **Export format** extensions
- **Real-time notifications**

#### 📚 Documentation
- **API documentation** improvements
- **Setup guides** for different environments
- **PowerBI tutorial** enhancements
- **Video tutorials** and examples

#### 🐛 Bug Fixes
- **SQL Server connectivity** issues
- **PowerBI refresh** problems
- **Data inconsistency** fixes
- **Performance bottlenecks**

## 🏗️ Architecture Guidelines

### Database Layer
- Use **SQLAlchemy ORM** for database operations
- Implement **connection pooling** for performance
- Add **proper error handling** for database exceptions
- Follow **financial data security** practices

### API Layer
- Follow **RESTful** design principles
- Use **Pydantic models** for request/response validation
- Implement **proper HTTP status codes**
- Add **comprehensive error responses**

### Business Logic
- Keep **business logic** separate from API layer
- Use **dependency injection** pattern
- Implement **proper logging** throughout
- Add **input validation** and sanitization

### Testing Strategy
- **Unit tests**: Individual function testing
- **Integration tests**: API endpoint testing
- **Performance tests**: Load and stress testing
- **Security tests**: SQL injection and auth testing

## 🚦 Review Process

### Automated Checks
- All tests must pass
- Code coverage > 80%
- No security vulnerabilities
- Performance benchmarks met

### Manual Review
- Code quality and readability
- Architecture compliance
- Documentation completeness
- Business logic correctness

## 📊 Performance Standards

### API Response Times
- **Health endpoints**: < 100ms
- **Simple queries**: < 500ms
- **Complex analysis**: < 5s
- **PowerBI endpoints**: < 2s

### Code Quality
- **Cyclomatic complexity**: < 10
- **Function length**: < 50 lines
- **Test coverage**: > 80%
- **Documentation**: 100% for public APIs

## 🤝 Community Guidelines

### Be Respectful
- Use inclusive language
- Be constructive in feedback
- Help newcomers get started
- Share knowledge and experience

### Communication Channels
- **Issues**: Bug reports and feature requests
- **Discussions**: General questions and ideas
- **Pull Requests**: Code contributions
- **Wiki**: Documentation improvements

## 📞 Getting Help

- **Documentation**: Check README.md and wiki
- **Issues**: Search existing issues first
- **Discussions**: Ask questions in GitHub Discussions
- **Code review**: Tag maintainers for urgent reviews

## 🎯 Contribution Recognition

Contributors will be:
- **Listed** in CONTRIBUTORS.md
- **Mentioned** in release notes
- **Invited** to maintainer team (active contributors)
- **Featured** in project showcase

---

Happy contributing! 🚀✨