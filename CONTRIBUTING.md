# Contributing to FinGenie

Thank you for your interest in contributing to FinGenie! This document provides guidelines for contributing to this research project.

## 🎯 Project Overview

FinGenie is a research implementation demonstrating multi-agent AI systems for financial advisory services. It was developed as part of academic research and presented at the ICLR 2025 Financial AI Workshop.

## 🤝 How to Contribute

### Reporting Issues

1. **Check existing issues** first to avoid duplicates
2. **Use the issue template** when creating new issues
3. **Provide detailed information**:
   - Environment details (OS, Python version, etc.)
   - Steps to reproduce the issue
   - Expected vs actual behavior
   - Error messages or logs
   - Screenshots if applicable

### Suggesting Enhancements

1. **Open an issue** to discuss the enhancement before implementing
2. **Explain the use case** and benefits
3. **Consider backward compatibility**
4. **Provide implementation ideas** if you have them

### Code Contributions

#### Getting Started

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create a new branch** for your feature/fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Set up the development environment**:
   ```bash
   pip install -r requirements.txt
   cp env.example .env
   # Add your API keys to .env
   ```

#### Development Guidelines

1. **Code Style**:
   - Follow PEP 8 conventions
   - Use meaningful variable and function names
   - Add docstrings to functions and classes
   - Keep functions focused and small

2. **Type Hints**:
   - Use type hints for function parameters and return values
   - Import types from `typing` module when needed

3. **Error Handling**:
   - Handle API failures gracefully
   - Provide informative error messages
   - Log errors appropriately

4. **Security**:
   - Never commit API keys or sensitive data
   - Use environment variables for configuration
   - Follow security best practices

#### Agent Development

When creating or modifying agents:

1. **Agent Structure**:
   ```python
   def create_agent_name():
       system_prompt = """Clear description of agent's role and responsibilities"""
       
       agent = ConversableAgent(
           name="Agent_Name",
           system_message=system_prompt,
           llm_config={
               "config_list": [{"model": "gpt-4", "api_key": get_openai_key()}]
           }
       )
       return agent
   ```

2. **System Prompts**:
   - Be specific about the agent's role
   - Include expected input/output formats
   - Provide context about the agent's place in the workflow

3. **Configuration**:
   - Use environment variables for API keys
   - Make model selection configurable
   - Include fallback options when possible

#### Testing

1. **Test Your Changes**:
   ```bash
   # Test individual agents
   python agents/your_agent.py
   
   # Test the full system
   python orchestrator_direct.py
   ```

2. **Add Tests** for new functionality:
   - Create test files in `agents/test/`
   - Test both success and failure cases
   - Mock API calls when appropriate

3. **Update Documentation** if needed

#### Submitting Changes

1. **Commit Messages**:
   - Use clear, descriptive commit messages
   - Start with a verb (Add, Fix, Update, Remove)
   - Keep the first line under 50 characters
   - Add details in the body if needed

2. **Pull Request**:
   - Create a pull request from your feature branch
   - Fill out the PR template completely
   - Link related issues
   - Include screenshots/logs if relevant

3. **Review Process**:
   - Address feedback from reviewers
   - Keep the PR updated with the main branch
   - Be patient and respectful during the review process

## 🔧 Development Setup

### Prerequisites

- Python 3.8+
- Git
- OpenAI API key
- Anthropic API key (optional)

### Local Development

1. **Clone and setup**:
   ```bash
   git clone https://github.com/yourusername/fingenie.git
   cd fingenie
   pip install -r requirements.txt
   ```

2. **Environment configuration**:
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

3. **Test the setup**:
   ```bash
   python agents/customer_chatbot.py
   ```

## 📝 Documentation

When contributing, please:

1. **Update relevant documentation**
2. **Add docstrings** to new functions
3. **Update the README** if adding new features
4. **Include examples** in your documentation

## 🚫 What Not to Contribute

Please avoid:

1. **Hardcoded API keys** or sensitive data
2. **Large binary files** without prior discussion
3. **Breaking changes** without discussion
4. **Code without proper error handling**
5. **Features that compromise security**

## 🔒 Security

- **Never commit sensitive data** (API keys, passwords, etc.)
- **Report security vulnerabilities** privately via email
- **Use secure coding practices**
- **Validate all inputs**

## 📄 License

By contributing, you agree that your contributions will be licensed under the GNU License.

## 🙋‍♂️ Questions?

- **General questions**: Open an issue with the "question" label
- **Security concerns**: Email the maintainers directly
- **Feature discussions**: Start with an issue before implementing

## 🎉 Recognition

Contributors will be acknowledged in:
- The repository's contributors list
- Release notes for significant contributions
- Academic acknowledgments where appropriate

Thank you for contributing to FinGenie! 🚀 