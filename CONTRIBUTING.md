# Contributing to Telecom AI Assistant

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/Telecom-ai-assistant.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Commit and push
7. Submit a pull request

## Development Setup

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
```

### Running Services

```bash
# Start development services
make dev

# Or manually
docker-compose -f docker-compose.dev.yml up -d
```

## Code Style

### Python (Backend)

- Follow PEP 8 guidelines
- Use type hints for all functions
- Write docstrings for classes and functions
- Format code with Black: `make format`
- Check with flake8: `make lint`

### TypeScript (Frontend)

- Follow TypeScript best practices
- Use functional components with hooks
- Write JSDoc comments for complex functions
- Format with Prettier: `npm run format`
- Lint with ESLint: `npm run lint`

## Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Commit Messages

Follow conventional commits:

- `feat: Add new feature`
- `fix: Fix bug`
- `docs: Update documentation`
- `style: Format code`
- `refactor: Refactor code`
- `test: Add tests`
- `chore: Update dependencies`

## Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all tests pass
4. Update README.md if needed
5. Request review from maintainers

## Areas for Contribution

### High Priority
- Complete voice component implementation
- Add more unit and integration tests
- Improve error handling
- Performance optimization

### Medium Priority
- Add more telecom-specific functions
- Implement user authentication
- Add more knowledge base documents
- Improve UI/UX

### Low Priority
- Add internationalization (i18n)
- Create mobile app
- Add analytics dashboard
- Implement A/B testing

## Code Review Guidelines

When reviewing code:
- Be respectful and constructive
- Focus on code quality and best practices
- Check for security issues
- Verify tests are included
- Ensure documentation is updated

## Questions?

Feel free to:
- Open an issue for questions
- Join discussions in GitHub Discussions
- Contact maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
