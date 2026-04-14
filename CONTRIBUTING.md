# Contributing to GuardRAG

Thank you for your interest in contributing to GuardRAG! We welcome contributions from the community to help make this privacy-first RAG tool better for everyone.

## Table of Contents
- [How Can I Contribute?](#how-can-i-contribute)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)
- [Pull Requests](#pull-requests)
- [Development Setup](#development-setup)
- [Code Style](#code-style)

## How Can I Contribute?

### Reporting Bugs
If you find a bug, please create a new issue on GitHub and include:
- A clear description of the problem.
- Steps to reproduce the issue.
- Your operating system and Python version.
- Any relevant logs or error messages.

### Feature Requests
We'd love to hear your ideas! Please open an issue and describe the feature you'd like to see, why it's useful, and any implementation thoughts you have.

### Pull Requests
If you're ready to contribute code:
1. Fork the repository.
2. Create a new branch (`git checkout -b feat/your-feature-name`).
3. Make your changes.
4. Add tests if applicable.
5. Commit your changes using [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).
6. Push to your fork and submit a pull request.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/sowmiyan-s/GUARD-RAG.git
   cd GUARD-RAG
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install in editable mode with development dependencies:
   ```bash
   pip install -e .
   pip install pytest pytest-cov
   ```

4. Run tests:
   ```bash
   pytest
   ```

## Code Style
- Follow PEP 8 guidelines.
- Use meaningful variable and function names.
- Include docstrings for new functions and classes.
- Ensure all tests pass before submitting.

## License
By contributing, you agree that your contributions will be licensed under the MIT License.
