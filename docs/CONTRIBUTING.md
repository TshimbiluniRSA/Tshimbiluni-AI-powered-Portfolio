# Contributing to Tshimbiluni AI-powered Portfolio

First off, thank you for considering contributing to this project! 🎉

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code.

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive criticism
- Accept responsibility and apologize for mistakes
- Focus on what is best for the community

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/Tshimbiluni-AI-powered-Portfolio.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Commit your changes
7. Push to your fork
8. Open a Pull Request

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker (optional but recommended)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r src/requirements.txt
cp .env.example .env
# Edit .env with your configuration
uvicorn src.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local with your configuration
npm run dev
```

### Using Docker

```bash
docker-compose -f docker-compose.dev.yml up
```

## How to Contribute

### Areas for Contribution

1. **Bug Fixes**: Check open issues for bugs
2. **Features**: Implement new features from the roadmap
3. **Documentation**: Improve README, add examples, write tutorials
4. **Tests**: Add unit tests, integration tests
5. **UI/UX**: Improve design, accessibility, user experience
6. **Performance**: Optimize code, reduce load times
7. **Translations**: Add i18n support, translate content

### Before You Start

- Check if an issue already exists for what you want to work on
- If not, create an issue to discuss your idea
- Wait for feedback before starting major work
- Keep changes focused and atomic

## Coding Standards

### Python (Backend)

- Follow PEP 8 style guide
- Use type hints
- Write docstrings for functions and classes
- Keep functions small and focused
- Use meaningful variable names

```python
def calculate_response_time(start_time: datetime, end_time: datetime) -> int:
    """
    Calculate response time in milliseconds.
    
    Args:
        start_time: The start timestamp
        end_time: The end timestamp
        
    Returns:
        Response time in milliseconds
    """
    return int((end_time - start_time).total_seconds() * 1000)
```

### TypeScript/React (Frontend)

- Use TypeScript for type safety
- Follow React best practices
- Use functional components and hooks
- Keep components small and reusable
- Use meaningful prop names

```typescript
interface ButtonProps {
  label: string;
  onClick: () => void;
  disabled?: boolean;
}

const Button: React.FC<ButtonProps> = ({ label, onClick, disabled = false }) => {
  return (
    <button onClick={onClick} disabled={disabled}>
      {label}
    </button>
  );
};
```

### Code Quality

- Run linters before committing
  - Backend: `flake8 src/`
  - Frontend: `npm run lint`
- Format code consistently
  - Backend: `black src/`
  - Frontend: `npm run format`
- Write tests for new features
- Ensure all tests pass

## Commit Messages

Follow the Conventional Commits specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```
feat(chat): add streaming response support

Implement server-sent events for real-time chat streaming.
This improves user experience by showing responses as they arrive.

Closes #123
```

```
fix(api): handle empty GitHub profile responses

Add validation and default values for missing profile data.

Fixes #456
```

## Pull Request Process

1. **Update Documentation**: Update README if needed
2. **Add Tests**: Ensure your code is tested
3. **Run Tests**: Make sure all tests pass
4. **Lint Your Code**: Run linters and fix issues
5. **Update Changelog**: Add entry to CHANGELOG.md (if exists)
6. **Create PR**: Write a clear description of your changes
7. **Link Issues**: Reference related issues
8. **Request Review**: Tag maintainers for review
9. **Address Feedback**: Make requested changes
10. **Squash Commits**: Clean up commit history if needed

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How has this been tested?

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed code
- [ ] Commented complex code
- [ ] Updated documentation
- [ ] No new warnings
- [ ] Added tests
- [ ] All tests pass
- [ ] Works on different browsers (frontend)
```

## Reporting Bugs

### Before Reporting

- Check if the bug has already been reported
- Verify it's reproducible in the latest version
- Collect relevant information

### Bug Report Template

```markdown
**Describe the bug**
A clear description of the bug.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What should happen.

**Screenshots**
If applicable, add screenshots.

**Environment**
- OS: [e.g., Ubuntu 22.04]
- Browser: [e.g., Chrome 120]
- Version: [e.g., 1.0.0]

**Additional context**
Any other relevant information.
```

## Suggesting Features

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution you'd like**
What you want to happen.

**Describe alternatives you've considered**
Other solutions you've thought about.

**Additional context**
Screenshots, mockups, or examples.
```

## Questions?

- Open a Discussion on GitHub
- Check existing documentation
- Ask in the community chat

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Given credit in commit history

Thank you for contributing! 🙏
