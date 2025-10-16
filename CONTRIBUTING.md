# Contributing to The Novelist

Thank you for considering contributing to The Novelist! 🎉

## Code of Conduct

Be respectful, constructive, and collaborative.

## How to Contribute

### Reporting Bugs

1. Check if the bug is already reported in [Issues](https://github.com/yourusername/the-novelist/issues)
2. If not, create a new issue with:
   - Clear title
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (OS, Python version)

### Suggesting Features

1. Check existing [Feature Requests](https://github.com/yourusername/the-novelist/issues?q=is%3Aissue+label%3Aenhancement)
2. Create a new issue with:
   - Clear description
   - Use cases
   - Mockups/examples (if applicable)

### Pull Requests

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit PR with clear description

## Development Setup
```bash
git clone https://github.com/yourusername/the-novelist.git
cd the-novelist
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
python -m spacy download it_core_news_sm
```

## Coding Standards

- Follow PEP 8
- Use meaningful variable names
- Add docstrings to all functions/classes
- Comment complex logic
- Keep functions small and focused

## Testing

Before submitting PR:
- Test all features manually
- Check for console errors
- Verify UI responsiveness

Thank you for contributing!