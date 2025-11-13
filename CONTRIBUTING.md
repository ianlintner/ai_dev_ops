# Contributing to AI DevOps

Thank you for your interest in contributing to the AI DevOps repository! This document provides guidelines for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Pull Request Process](#pull-request-process)
- [Adding New Examples](#adding-new-examples)
- [Adding New Integrations](#adding-new-integrations)

## Code of Conduct

By participating in this project, you agree to:
- Be respectful and inclusive
- Welcome newcomers and help them get started
- Accept constructive criticism gracefully
- Focus on what is best for the community

## How to Contribute

### Reporting Issues

If you find a bug or have a suggestion:

1. Check if the issue already exists in [GitHub Issues](https://github.com/ianlintner/ai_dev_ops/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Your environment details (OS, Python version, etc.)

### Suggesting Features

Feature requests are welcome! Please:
- Explain the use case
- Describe how it would work
- Provide examples if possible

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- pip

### Setting Up Your Environment

1. Fork the repository on GitHub

2. Clone your fork:
```bash
git clone https://github.com/YOUR_USERNAME/ai_dev_ops.git
cd ai_dev_ops
```

3. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create a branch for your changes:
```bash
git checkout -b feature/your-feature-name
```

## Coding Standards

### Python Code Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and short
- Use type hints where appropriate

Example:
```python
def calculate_inference_cost(
    tokens_used: int,
    model_name: str,
    token_price: float = 0.00002
) -> float:
    """
    Calculate the cost of an AI inference.
    
    Args:
        tokens_used: Number of tokens consumed
        model_name: Name of the AI model
        token_price: Price per token in dollars
    
    Returns:
        Total cost in dollars
    """
    return tokens_used * token_price
```

### Documentation

- Use clear, concise language
- Include code examples
- Provide context and explain why, not just what
- Keep documentation up to date with code changes

### File Organization

Place files in the appropriate directory:
- `examples/` - Runnable code examples
- `integrations/` - Platform integration configs
- `data-formats/` - Schema definitions and examples
- `docs/` - Documentation files

## Pull Request Process

### Before Submitting

1. Test your changes:
```bash
# Test Python examples
python examples/your_example.py

# Validate JSON files
python -c "import json; json.load(open('your-file.json'))"
```

2. Ensure code quality:
```bash
# Check Python syntax
python -m py_compile your_file.py

# Run any existing tests
pytest tests/
```

3. Update documentation:
   - Update README.md if needed
   - Add/update relevant documentation in `docs/`
   - Update example READMEs

4. Commit your changes:
```bash
git add .
git commit -m "Add: Brief description of your changes"
```

### Commit Message Guidelines

Use clear, descriptive commit messages:
- `Add: ...` - New feature or file
- `Fix: ...` - Bug fix
- `Update: ...` - Update to existing feature
- `Docs: ...` - Documentation changes
- `Refactor: ...` - Code refactoring

Examples:
- `Add: OpenTelemetry example for Claude integration`
- `Fix: Incorrect metric name in Prometheus example`
- `Update: Grafana dashboard with cost tracking panel`
- `Docs: Improve Azure Monitor setup instructions`

### Submitting Your Pull Request

1. Push to your fork:
```bash
git push origin feature/your-feature-name
```

2. Go to the original repository on GitHub and create a Pull Request

3. In your PR description:
   - Describe what changed and why
   - Reference any related issues
   - Include screenshots for visual changes
   - List any breaking changes

4. Wait for review:
   - Respond to feedback promptly
   - Make requested changes
   - Be patient and respectful

## Adding New Examples

When adding a new example:

### Structure

```
examples/
└── your-category/
    ├── README.md
    ├── example_1.py
    └── example_2.py
```

### README Template

```markdown
# Category Name Examples

Brief description of what this category covers.

## Files

- `example_1.py`: Description
- `example_2.py`: Description

## Running Examples

\`\`\`bash
python example_1.py
\`\`\`

## Prerequisites

List any special requirements or setup needed.

## Key Concepts

Explain important concepts demonstrated.
```

### Example Code Template

```python
"""
Brief description of what this example demonstrates.

This example shows:
- Key feature 1
- Key feature 2
- Key feature 3
"""

# Imports with comments
from opentelemetry import trace  # For distributed tracing

# Configuration
CONFIG = {
    "service_name": "example-service",
    "environment": "development"
}

def main():
    """Main example function."""
    # Your example code here
    pass

if __name__ == "__main__":
    print("Example Name")
    print("=" * 50)
    main()
```

### Example Requirements

- Must be runnable standalone
- Should include clear comments
- Must handle errors gracefully
- Should print meaningful output
- Include docstrings

## Adding New Integrations

When adding a new integration:

### Structure

```
integrations/
└── platform-name/
    ├── README.md
    ├── config-example.json  (if applicable)
    └── setup-script.sh      (if applicable)
```

### Integration README Template

```markdown
# Platform Name Integration

Brief description of the integration.

## Setup

### Prerequisites
- Requirement 1
- Requirement 2

### Installation

\`\`\`bash
# Installation commands
\`\`\`

### Configuration

\`\`\`bash
# Configuration steps
\`\`\`

## Usage

Explain how to use the integration.

## Best Practices

List platform-specific best practices.

## Troubleshooting

Common issues and solutions.

## Resources

- [Platform Documentation](url)
- [API Reference](url)
```

## Adding Data Formats

When adding new data format schemas:

1. Create JSON Schema file
2. Add examples file
3. Validate both:
```bash
python -c "import json; json.load(open('schema.json'))"
python -c "import json; json.load(open('examples.json'))"
```

## Questions?

If you have questions:
- Open a [GitHub Discussion](https://github.com/ianlintner/ai_dev_ops/discussions)
- Comment on a related issue
- Reach out to maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes
- README acknowledgments (for significant contributions)

Thank you for contributing to AI DevOps! 🎉
