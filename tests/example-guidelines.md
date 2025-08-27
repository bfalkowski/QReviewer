# Project Code Review Guidelines

## Security
- Always validate and sanitize user inputs
- Use parameterized queries for database operations
- Escape HTML output to prevent XSS attacks
- Avoid storing sensitive data in logs or error messages

## Performance
- Prefer list comprehensions over explicit loops when appropriate
- Use generators for large data processing
- Avoid N+1 query problems in database operations
- Cache expensive computations when possible

## Code Quality
- Follow PEP 8 style guidelines
- Use descriptive variable and function names
- Keep functions small and focused (max 20 lines)
- Add type hints for all public functions

## Testing
- Aim for >90% test coverage
- Test edge cases and error conditions
- Use descriptive test names
- Mock external dependencies

## Documentation
- Add docstrings to all public functions and classes
- Update README.md when adding new features
- Include examples in docstrings
- Document any non-obvious business logic
