# Contributing to SmartPlanner

Thank you for your interest in contributing to SmartPlanner! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other contributors

## How to Contribute

There are many ways to contribute to SmartPlanner:

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/shrek3075/hackcamp/issues)
2. If not, create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots (if applicable)
   - Environment details (OS, browser, versions)

### Suggesting Enhancements

1. Check existing [Issues](https://github.com/shrek3075/hackcamp/issues) for similar suggestions
2. Create a new issue with:
   - Clear description of the enhancement
   - Use case and benefits
   - Possible implementation approach
   - Any relevant examples or mockups

### Contributing Code

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Test thoroughly
5. Commit with clear messages
6. Push to your fork
7. Create a Pull Request

## Development Setup

### Prerequisites

- Python 3.9+
- Node.js 18+
- Git
- OpenAI API key
- Supabase account

### Backend Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/hackcamp.git
cd hackcamp

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your credentials

# Run backend
python -m uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend/study-planner-pro

# Install dependencies
npm install

# Run development server
npm run dev
```

## Coding Standards

### Python (Backend)

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints where possible
- Write docstrings for functions and classes
- Keep functions focused and small
- Use meaningful variable names

**Example:**
```python
def calculate_study_hours(
    topics: List[str],
    difficulty: str
) -> float:
    """
    Calculate estimated study hours for given topics.

    Args:
        topics: List of topic names
        difficulty: Difficulty level ('easy', 'medium', 'hard')

    Returns:
        Estimated hours as float
    """
    # Implementation
```

### TypeScript/React (Frontend)

- Follow [React best practices](https://react.dev/learn)
- Use TypeScript for type safety
- Use functional components with hooks
- Keep components small and focused
- Use meaningful component and variable names
- Follow existing naming conventions

**Example:**
```typescript
interface StudyPlan {
  id: string;
  subject: string;
  testDate: string;
}

const PlanCard: React.FC<{ plan: StudyPlan }> = ({ plan }) => {
  const [isLoading, setIsLoading] = useState(false);

  // Component logic

  return (
    // JSX
  );
};
```

### General Guidelines

- **DRY**: Don't Repeat Yourself - extract common logic
- **KISS**: Keep It Simple, Stupid - avoid over-engineering
- **Comments**: Explain why, not what (code should be self-documenting)
- **Error Handling**: Always handle errors gracefully
- **Security**: Never commit API keys or secrets

## Commit Messages

Write clear, descriptive commit messages following this format:

```
<type>: <subject>

<body (optional)>

<footer (optional)>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting (not CSS)
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

### Examples

```
feat: Add calendar integration for study planning

- Parse .ics files using ical.js
- Calculate free time slots with 15-min buffers
- Integrate with study plan generation

Closes #42
```

```
fix: Resolve quiz generation from notes

Updated AI prompt to strictly use note content instead of
generating generic questions.
```

## Pull Request Process

1. **Before Submitting:**
   - Test your changes thoroughly
   - Update documentation if needed
   - Ensure code follows style guidelines
   - Rebase on latest main branch

2. **PR Description Should Include:**
   - What changes were made and why
   - Issue number (if applicable)
   - Screenshots (for UI changes)
   - Breaking changes (if any)
   - Testing performed

3. **PR Template:**
   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Refactoring

   ## Related Issue
   Fixes #(issue number)

   ## Testing
   - [ ] Tested locally
   - [ ] Added/updated tests
   - [ ] All tests passing

   ## Screenshots (if applicable)

   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Documentation updated
   - [ ] No breaking changes (or documented)
   ```

4. **Review Process:**
   - At least one approval required
   - Address all review comments
   - Keep PR focused and atomic
   - Squash commits if needed

## Testing

### Backend Tests

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

### Frontend Tests

```bash
cd frontend/study-planner-pro

# Run tests
npm test

# Run with coverage
npm test -- --coverage
```

### Manual Testing

1. Test all affected features
2. Test on multiple browsers (Chrome, Firefox, Safari)
3. Test error cases and edge cases
4. Verify API responses and error handling

## Project Structure

Before contributing, familiarize yourself with the project structure:

```
HackCamp/
├── app/                    # Backend (FastAPI)
│   ├── routes/            # API endpoints
│   ├── services/          # Business logic
│   └── clients/           # External services
│
├── frontend/              # Frontend (React)
│   └── study-planner-pro/
│       ├── src/
│       │   ├── pages/     # Page components
│       │   └── components/# Reusable components
│       └── supabase/functions/  # Edge functions
│
└── docs/                  # Documentation
```

## Questions?

If you have questions:

1. Check existing [Issues](https://github.com/shrek3075/hackcamp/issues)
2. Review [Documentation](README.md)
3. Create a new issue with your question

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to SmartPlanner!
